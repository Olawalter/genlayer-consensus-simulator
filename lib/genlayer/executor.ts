"use client";

import { getClient } from "./client";
import type { RealConsensusResult, ValidatorVote } from "./types";
import { TransactionStatus } from "genlayer-js/types";

export type OnProgress = (status: string, detail?: string) => void;

/**
 * Deploy a GenLayer Intelligent Contract and call its first write method.
 * Returns real validator votes and consensus result from Studio Net.
 */
export async function executeOnChain(
  contractCode: string,
  functionName: string,
  args: unknown[],
  onProgress?: OnProgress
): Promise<RealConsensusResult> {
  const client = getClient();
  const startMs = Date.now();

  // Step 1 — Deploy
  onProgress?.("deploying", "Deploying contract to Studio Net...");
  const deployHash = await client.deployContract({
    code: contractCode,
    args: [],
    leaderOnly: false,
  });
  onProgress?.("deploy_submitted", `Deploy tx: ${deployHash}`);

  // Step 2 — Wait for deploy to be accepted
  onProgress?.("waiting_deploy", "Waiting for deploy consensus...");
  const deployReceipt = await client.waitForTransactionReceipt({
    hash: deployHash as `0x${string}` & { length: 66 },
    status: TransactionStatus.ACCEPTED,
    retries: 60,
    interval: 2000,
  });

  const contractAddress = (deployReceipt as unknown as { to_address?: string })?.to_address
    ?? (deployReceipt as unknown as { recipient?: string })?.recipient
    ?? "";

  onProgress?.("deployed", `Contract at ${contractAddress}`);

  if (!contractAddress) {
    throw new Error("Could not determine deployed contract address from receipt");
  }

  // Step 3 — Call the write function
  onProgress?.("calling", `Calling ${functionName}(${args.map(String).join(", ")})...`);
  const callHash = await client.writeContract({
    address: contractAddress as `0x${string}`,
    functionName,
    args: args as unknown[] as never[],
    value: BigInt(0),
    leaderOnly: false,
  });
  onProgress?.("call_submitted", `Call tx: ${callHash}`);

  // Step 4 — Wait for call consensus
  onProgress?.("waiting_consensus", "Validators executing and voting...");
  const callReceipt = await client.waitForTransactionReceipt({
    hash: callHash as `0x${string}` & { length: 66 },
    status: TransactionStatus.ACCEPTED,
    retries: 60,
    interval: 2000,
  });

  onProgress?.("finalized", "Consensus reached");

  // Step 5 — Parse receipt into our result shape
  return parseReceipt(callReceipt, callHash, contractAddress, startMs);
}

/**
 * Call a write method on an already-deployed contract.
 */
export async function callOnChain(
  contractAddress: string,
  functionName: string,
  args: unknown[],
  onProgress?: OnProgress
): Promise<RealConsensusResult> {
  const client = getClient();
  const startMs = Date.now();

  onProgress?.("calling", `Calling ${functionName} on ${contractAddress.slice(0, 10)}...`);

  const callHash = await client.writeContract({
    address: contractAddress as `0x${string}`,
    functionName,
    args: args as unknown[] as never[],
    value: BigInt(0),
    leaderOnly: false,
  });

  onProgress?.("waiting_consensus", "Validators executing and voting...");

  const receipt = await client.waitForTransactionReceipt({
    hash: callHash as `0x${string}` & { length: 66 },
    status: TransactionStatus.ACCEPTED,
    retries: 60,
    interval: 2000,
  });

  onProgress?.("finalized", "Consensus reached");
  return parseReceipt(receipt, callHash, contractAddress, startMs);
}

/**
 * Read contract state (no consensus needed).
 */
export async function readOnChain(
  contractAddress: string,
  functionName: string,
  args: unknown[] = []
): Promise<unknown> {
  const client = getClient();
  return client.readContract({
    address: contractAddress as `0x${string}`,
    functionName,
    args: args as unknown[] as never[],
  });
}

// ── helpers ───────────────────────────────────────────────────────────────────

function parseReceipt(
  receipt: Record<string, unknown>,
  txHash: string,
  contractAddress: string,
  startMs: number
): RealConsensusResult {
  const statusName = (receipt.statusName ?? receipt.status ?? "UNKNOWN") as string;
  const consensusData = receipt.consensus_data as {
    final?: boolean;
    leader_receipt?: Record<string, unknown>[];
    validators?: Record<string, unknown>[];
    votes?: Record<string, string>;
  } | undefined;

  const leaderReceiptRaw = consensusData?.leader_receipt?.[0];
  const leaderReceipt = leaderReceiptRaw ? {
    result:           String(leaderReceiptRaw.result ?? ""),
    execution_result: String(leaderReceiptRaw.execution_result ?? ""),
    mode:             String(leaderReceiptRaw.mode ?? ""),
    eq_outputs:       (leaderReceiptRaw.eq_outputs ?? {}) as Record<string, unknown>,
    error:            leaderReceiptRaw.error ? String(leaderReceiptRaw.error) : null,
  } : null;

  // Build per-validator vote list from lastRound
  const lastRound = receipt.lastRound as {
    roundValidators?: string[];
    validatorVotesName?: string[];
  } | undefined;

  const validators: ValidatorVote[] = [];
  if (lastRound?.roundValidators) {
    lastRound.roundValidators.forEach((addr, i) => {
      validators.push({
        address: addr,
        vote: (lastRound.validatorVotesName?.[i] ?? "NOT_VOTED") as ValidatorVote["vote"],
        executionResult: "",
      });
    });
  }

  const agreeCount   = validators.filter((v) => v.vote === "AGREE").length;
  const disagreeCount = validators.filter((v) => v.vote === "DISAGREE").length;
  const total = validators.length;

  const accepted = ["ACCEPTED", "FINALIZED", "READY_TO_FINALIZE"].includes(statusName);
  const rejected = statusName === "UNDETERMINED" || disagreeCount > agreeCount;

  const finalOutcome: RealConsensusResult["finalOutcome"] = accepted
    ? "ACCEPTED"
    : rejected
    ? "REJECTED"
    : total === 0
    ? "PENDING"
    : "SPLIT";

  return {
    txHash,
    status: statusName,
    finalOutcome,
    consensusReached: accepted,
    leaderReceipt,
    validators,
    totalValidators: total,
    agreeCount,
    disagreeCount,
    contractAddress,
    elapsedMs: Date.now() - startMs,
  };
}
