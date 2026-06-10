export interface ConsensusResult {
  simulationId: string;
  round: number;
  acceptCount: number;
  rejectCount: number;
  uncertainCount: number;
  consensusType: 'unanimous' | 'majority' | 'split' | null;
  equivalencePass: boolean;
  outcome: 'ACCEPTED' | 'REJECTED' | 'APPEAL_TRIGGERED';
}
