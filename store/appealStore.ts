import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { SimulationRun } from "@/services/simulationService";
import type { EquivalenceResult } from "@/lib/validators/equivalence";

export type AppealStatus = "pending" | "in_progress" | "resolved_accept" | "resolved_reject" | "escalated";

export interface AppealRound {
  roundNumber: number;
  validatorCount: number;
  votes: { name: string; vote: "ACCEPT" | "REJECT" | "UNCERTAIN"; confidence: number }[];
  equivalenceResult: EquivalenceResult;
  outcome: "ACCEPTED" | "REJECTED" | "APPEAL_TRIGGERED";
  durationMs: number;
}

export interface AppealRecord {
  id: string;
  simulationId: string;
  claim: string;
  category: string;
  appealReason: string;
  status: AppealStatus;
  rounds: AppealRound[];
  createdAt: number;
  resolvedAt: number | null;
  finalOutcome: "ACCEPTED" | "REJECTED" | null;
}

interface AppealStore {
  appeals: AppealRecord[];
  activeAppealId: string | null;

  createAppeal: (run: SimulationRun, reason: string) => string;
  addRound: (appealId: string, round: AppealRound) => void;
  resolveAppeal: (appealId: string, outcome: "ACCEPTED" | "REJECTED") => void;
  setActiveAppeal: (id: string | null) => void;
  clearAppeals: () => void;
}

export const useAppealStore = create<AppealStore>()(
  persist(
    (set, get) => ({
      appeals: [],
      activeAppealId: null,

      createAppeal: (run, reason) => {
        const id = `appeal_${Date.now()}`;

        // Build round 1 from the original simulation data
        const round1: AppealRound = {
          roundNumber: 1,
          validatorCount: run.validators.filter((v) => v.vote !== null).length,
          votes: run.validators
            .filter((v) => v.vote !== null)
            .map((v) => ({ name: v.name, vote: v.vote!, confidence: v.confidence ?? 0 })),
          equivalenceResult: run.consensusResult!,
          outcome: run.consensusResult!.outcome,
          durationMs: Date.now() - run.startedAt,
        };

        const record: AppealRecord = {
          id,
          simulationId: run.id,
          claim: run.claim,
          category: run.category,
          appealReason: reason,
          status: "in_progress",
          rounds: [round1],
          createdAt: Date.now(),
          resolvedAt: null,
          finalOutcome: null,
        };

        set((s) => ({ appeals: [record, ...s.appeals], activeAppealId: id }));
        return id;
      },

      addRound: (appealId, round) =>
        set((s) => ({
          appeals: s.appeals.map((a) =>
            a.id === appealId ? { ...a, rounds: [...a.rounds, round] } : a
          ),
        })),

      resolveAppeal: (appealId, outcome) =>
        set((s) => ({
          appeals: s.appeals.map((a) =>
            a.id === appealId
              ? {
                  ...a,
                  status: outcome === "ACCEPTED" ? "resolved_accept" : "resolved_reject",
                  finalOutcome: outcome,
                  resolvedAt: Date.now(),
                }
              : a
          ),
        })),

      setActiveAppeal: (id) => set({ activeAppealId: id }),

      clearAppeals: () => set({ appeals: [], activeAppealId: null }),
    }),
    { name: "appeals-arena-store", partialize: (s) => ({ appeals: s.appeals }) }
  )
);
