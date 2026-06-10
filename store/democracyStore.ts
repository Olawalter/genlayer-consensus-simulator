import { create } from "zustand";
import { persist } from "zustand/middleware";

export type TxLifecycleStage =
  | "proposed"
  | "validator_review"
  | "equivalence_check"
  | "finality_window"
  | "challenge_period"
  | "finalized"
  | "appealed"
  | "rejected";

export interface DemocracyTransaction {
  id: string;
  claim: string;
  category: string;
  proposer: string;
  stage: TxLifecycleStage;
  validatorVotes: { name: string; vote: "ACCEPT" | "REJECT" | "UNCERTAIN"; confidence: number }[];
  equivalenceScore: number;
  round: number;
  finalityCountdownMs: number;
  startedAt: number;
  finalizedAt: number | null;
  outcome: "ACCEPTED" | "REJECTED" | "PENDING" | "APPEALED";
  blockHeight: number;
  txHash: string;
}

interface DemocracyStore {
  transactions: DemocracyTransaction[];
  activeId: string | null;
  networkStats: {
    totalTx: number;
    accepted: number;
    rejected: number;
    appealed: number;
    avgFinalityMs: number;
    currentBlock: number;
  };

  addTransaction: (tx: DemocracyTransaction) => void;
  updateTransaction: (id: string, patch: Partial<DemocracyTransaction>) => void;
  setActiveId: (id: string | null) => void;
  incrementBlock: () => void;
  clearTransactions: () => void;
}

export const useDemocracyStore = create<DemocracyStore>()(
  persist(
    (set) => ({
      transactions: [],
      activeId: null,
      networkStats: {
        totalTx:      0,
        accepted:     0,
        rejected:     0,
        appealed:     0,
        avgFinalityMs: 0,
        currentBlock: 14_400,
      },

      addTransaction: (tx) =>
        set((s) => ({
          transactions: [tx, ...s.transactions].slice(0, 50),
          activeId: tx.id,
          networkStats: {
            ...s.networkStats,
            totalTx: s.networkStats.totalTx + 1,
            currentBlock: s.networkStats.currentBlock + 1,
          },
        })),

      updateTransaction: (id, patch) =>
        set((s) => {
          const txs = s.transactions.map((t) => (t.id === id ? { ...t, ...patch } : t));
          // recompute stats on finalize
          const finalized = txs.filter((t) => t.finalizedAt !== null);
          const accepted  = txs.filter((t) => t.outcome === "ACCEPTED").length;
          const rejected  = txs.filter((t) => t.outcome === "REJECTED").length;
          const appealed  = txs.filter((t) => t.outcome === "APPEALED").length;
          const avgMs = finalized.length
            ? finalized.reduce((sum, t) => sum + (t.finalizedAt! - t.startedAt), 0) / finalized.length
            : s.networkStats.avgFinalityMs;
          return {
            transactions: txs,
            networkStats: { ...s.networkStats, accepted, rejected, appealed, avgFinalityMs: avgMs },
          };
        }),

      setActiveId: (id) => set({ activeId: id }),

      incrementBlock: () =>
        set((s) => ({
          networkStats: { ...s.networkStats, currentBlock: s.networkStats.currentBlock + 1 },
        })),

      clearTransactions: () =>
        set({
          transactions: [],
          activeId: null,
          networkStats: { totalTx: 0, accepted: 0, rejected: 0, appealed: 0, avgFinalityMs: 0, currentBlock: 14_400 },
        }),
    }),
    { name: "democracy-store", partialize: (s) => ({ transactions: s.transactions, networkStats: s.networkStats }) }
  )
);
