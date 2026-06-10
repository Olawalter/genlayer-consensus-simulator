export interface Validator {
  id: string;
  name: string;
  model: string;
  persona: string;
  isActive: boolean;
}

export interface ValidatorVote {
  validatorId: string;
  simulationId: string;
  role: 'leader' | 'validator';
  vote: 'ACCEPT' | 'REJECT' | 'UNCERTAIN';
  confidence: number;
  reasoning: string;
  equivalenceScore: number;
}
