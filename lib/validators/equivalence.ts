import type { ValidatorVote } from "@/types/validator";

export interface EquivalenceResult {
  score: number;          // 0–1: how equivalent the votes are
  pass: boolean;          // whether equivalence threshold is met
  consensusType: "unanimous" | "majority" | "split";
  acceptCount: number;
  rejectCount: number;
  uncertainCount: number;
  outcome: "ACCEPTED" | "REJECTED" | "APPEAL_TRIGGERED";
  explanation: string;
}

const EQUIVALENCE_THRESHOLD = 0.6; // 60% agreement needed

export function computeEquivalence(votes: ValidatorVote[]): EquivalenceResult {
  const total = votes.length;
  if (total === 0) {
    return {
      score: 0, pass: false, consensusType: "split",
      acceptCount: 0, rejectCount: 0, uncertainCount: 0,
      outcome: "APPEAL_TRIGGERED", explanation: "No votes cast.",
    };
  }

  const acceptCount   = votes.filter((v) => v.vote === "ACCEPT").length;
  const rejectCount   = votes.filter((v) => v.vote === "REJECT").length;
  const uncertainCount = votes.filter((v) => v.vote === "UNCERTAIN").length;

  const maxCount = Math.max(acceptCount, rejectCount);
  const score = maxCount / total;

  const pass = score >= EQUIVALENCE_THRESHOLD;

  let consensusType: EquivalenceResult["consensusType"];
  if (score === 1) consensusType = "unanimous";
  else if (pass)   consensusType = "majority";
  else             consensusType = "split";

  let outcome: EquivalenceResult["outcome"];
  if (!pass) {
    outcome = "APPEAL_TRIGGERED";
  } else if (acceptCount >= rejectCount) {
    outcome = "ACCEPTED";
  } else {
    outcome = "REJECTED";
  }

  const explanation = buildExplanation(acceptCount, rejectCount, uncertainCount, total, score, pass);

  return { score, pass, consensusType, acceptCount, rejectCount, uncertainCount, outcome, explanation };
}

function buildExplanation(
  accept: number, reject: number, uncertain: number, total: number, score: number, pass: boolean
): string {
  const pct = Math.round(score * 100);
  if (!pass) {
    return `Validator outputs are too divergent (${pct}% agreement). The Equivalence Principle requires at least 60% agreement. An appeal round is triggered.`;
  }
  if (score === 1) {
    return `All ${total} validators reached identical conclusions — a unanimous consensus under the Equivalence Principle.`;
  }
  const majority = Math.max(accept, reject);
  return `${majority}/${total} validators (${pct}%) reached equivalent conclusions — within the Equivalence Principle threshold. Consensus is accepted.`;
}

export function computeEquivalenceScore(votes: ValidatorVote[]): number {
  const result = computeEquivalence(votes);
  return result.score;
}
