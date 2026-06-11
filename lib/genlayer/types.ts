export interface ValidatorVote {
  address: string;
  vote: "AGREE" | "DISAGREE" | "TIMEOUT" | "NOT_VOTED" | "DETERMINISTIC_VIOLATION";
  executionResult: string;
}

export interface RealConsensusResult {
  txHash: string;
  status: string;
  finalOutcome: "ACCEPTED" | "REJECTED" | "SPLIT" | "PENDING";
  consensusReached: boolean;
  leaderReceipt: {
    result: string;
    execution_result: string;
    mode: string;
    eq_outputs: Record<string, unknown>;
    error: string | null;
  } | null;
  validators: ValidatorVote[];
  totalValidators: number;
  agreeCount: number;
  disagreeCount: number;
  contractAddress?: string;
  elapsedMs: number;
}
