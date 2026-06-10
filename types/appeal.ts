export interface Appeal {
  id: string;
  simulationId: string;
  reason: string;
  status: 'open' | 'resolved' | 'rejected';
  originalOutcome: string;
  finalOutcome: string | null;
  createdAt: string;
}
