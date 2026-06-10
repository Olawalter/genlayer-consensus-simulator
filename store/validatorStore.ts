import { create } from "zustand";
import { persist } from "zustand/middleware";
import { VALIDATOR_PERSONAS, type ValidatorPersonaConfig } from "@/lib/validators/personas";

export interface CustomValidator extends ValidatorPersonaConfig {
  id: string;
  isCustom: boolean;
  createdAt: number;
  voteHistory: VoteRecord[];
  totalVotes: number;
  acceptRate: number;
  rejectRate: number;
  uncertainRate: number;
  avgConfidence: number;
}

export interface VoteRecord {
  id: string;
  claim: string;
  category: string;
  vote: "ACCEPT" | "REJECT" | "UNCERTAIN";
  confidence: number;
  reasoning: string;
  simulationId: string;
  timestamp: number;
}

interface ValidatorStore {
  validators: CustomValidator[];
  selectedValidatorId: string | null;
  comparisonIds: string[];

  selectValidator: (id: string) => void;
  toggleComparison: (id: string) => void;
  clearComparison: () => void;
  updateValidator: (id: string, patch: Partial<ValidatorPersonaConfig>) => void;
  resetValidator: (id: string) => void;
  addVoteRecord: (validatorId: string, record: Omit<VoteRecord, "id" | "timestamp">) => void;
  clearHistory: (validatorId: string) => void;
}

function seedValidators(): CustomValidator[] {
  return VALIDATOR_PERSONAS.map((p, i) => ({
    ...p,
    id: `default_${i}`,
    isCustom: false,
    createdAt: Date.now(),
    voteHistory: [],
    totalVotes: 0,
    acceptRate: 0,
    rejectRate: 0,
    uncertainRate: 0,
    avgConfidence: p.confidenceBase,
  }));
}

function recomputeStats(v: CustomValidator): CustomValidator {
  const h = v.voteHistory;
  if (h.length === 0) return { ...v, totalVotes: 0, acceptRate: 0, rejectRate: 0, uncertainRate: 0, avgConfidence: v.confidenceBase };
  const total = h.length;
  const accept    = h.filter((r) => r.vote === "ACCEPT").length;
  const reject    = h.filter((r) => r.vote === "REJECT").length;
  const uncertain = h.filter((r) => r.vote === "UNCERTAIN").length;
  const avgConf   = h.reduce((s, r) => s + r.confidence, 0) / total;
  return {
    ...v,
    totalVotes:    total,
    acceptRate:    accept    / total,
    rejectRate:    reject    / total,
    uncertainRate: uncertain / total,
    avgConfidence: avgConf,
  };
}

export const useValidatorStore = create<ValidatorStore>()(
  persist(
    (set) => ({
      validators: seedValidators(),
      selectedValidatorId: null,
      comparisonIds: [],

      selectValidator: (id) => set({ selectedValidatorId: id }),

      toggleComparison: (id) =>
        set((state) => {
          const already = state.comparisonIds.includes(id);
          if (already) return { comparisonIds: state.comparisonIds.filter((x) => x !== id) };
          if (state.comparisonIds.length >= 3) return state; // max 3 at once
          return { comparisonIds: [...state.comparisonIds, id] };
        }),

      clearComparison: () => set({ comparisonIds: [] }),

      updateValidator: (id, patch) =>
        set((state) => ({
          validators: state.validators.map((v) =>
            v.id === id ? { ...v, ...patch, isCustom: true } : v
          ),
        })),

      resetValidator: (id) =>
        set((state) => {
          const idx = state.validators.findIndex((v) => v.id === id);
          if (idx === -1) return state;
          const defaultIdx = parseInt(id.replace("default_", ""), 10);
          const original = VALIDATOR_PERSONAS[defaultIdx] ?? VALIDATOR_PERSONAS[0];
          return {
            validators: state.validators.map((v) =>
              v.id === id ? { ...v, ...original, isCustom: false } : v
            ),
          };
        }),

      addVoteRecord: (validatorId, record) =>
        set((state) => ({
          validators: state.validators.map((v) => {
            if (v.id !== validatorId) return v;
            const newRecord: VoteRecord = { ...record, id: `vr_${Date.now()}`, timestamp: Date.now() };
            const updated: CustomValidator = { ...v, voteHistory: [newRecord, ...v.voteHistory].slice(0, 50) };
            return recomputeStats(updated);
          }),
        })),

      clearHistory: (validatorId) =>
        set((state) => ({
          validators: state.validators.map((v) =>
            v.id === validatorId ? recomputeStats({ ...v, voteHistory: [] }) : v
          ),
        })),
    }),
    {
      name: "validator-lab-store",
      partialize: (s) => ({ validators: s.validators }),
    }
  )
);
