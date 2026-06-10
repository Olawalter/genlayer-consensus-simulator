import { create } from "zustand";
import type { LLMResponse } from "@/lib/llm/simulator";

export interface ComparisonRun {
  id: string;
  claim: string;
  responses: Record<string, LLMResponse>;
  startedAt: number;
  completedAt: number | null;
}

interface LLMCompareStore {
  currentRun: ComparisonRun | null;
  history: ComparisonRun[];
  loadingModelIds: string[];
  selectedModelId: string | null;

  startRun: (claim: string) => string;
  updateResponses: (runId: string, responses: Partial<Record<string, LLMResponse>>, loadingIds: string[]) => void;
  finalizeRun: (runId: string, responses: Record<string, LLMResponse>) => void;
  selectModel: (id: string | null) => void;
  clearHistory: () => void;
}

export const useLLMCompareStore = create<LLMCompareStore>((set) => ({
  currentRun: null,
  history: [],
  loadingModelIds: [],
  selectedModelId: null,

  startRun: (claim) => {
    const id = `cmp_${Date.now()}`;
    const run: ComparisonRun = { id, claim, responses: {}, startedAt: Date.now(), completedAt: null };
    set({ currentRun: run, loadingModelIds: [], selectedModelId: null });
    return id;
  },

  updateResponses: (runId, responses, loadingIds) =>
    set((s) => {
      if (s.currentRun?.id !== runId) return s;
      return {
        currentRun: { ...s.currentRun, responses: { ...s.currentRun.responses, ...responses } as Record<string, LLMResponse> },
        loadingModelIds: loadingIds,
      };
    }),

  finalizeRun: (runId, responses) =>
    set((s) => {
      if (s.currentRun?.id !== runId) return s;
      const finalized = { ...s.currentRun, responses, completedAt: Date.now() };
      return {
        currentRun: finalized,
        loadingModelIds: [],
        history: [finalized, ...s.history].slice(0, 10),
      };
    }),

  selectModel: (id) => set({ selectedModelId: id }),
  clearHistory: () => set({ history: [] }),
}));
