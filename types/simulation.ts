export interface Simulation {
  id: string;
  claimId: string;
  status: 'pending' | 'running' | 'accepted' | 'rejected' | 'appealed' | 'finalized';
  validatorCount: number;
  consensusReached: boolean | null;
  finalVerdict: string | null;
  createdAt: string;
}
