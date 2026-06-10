import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { SandboxExecutionResult } from "@/lib/sandbox/executor";

interface SandboxStore {
  code: string;
  activeTemplateId: string | null;
  functionInput: string;
  isRunning: boolean;
  currentResult: SandboxExecutionResult | null;
  history: SandboxExecutionResult[];
  selectedValidatorIndex: number | null;

  setCode: (code: string) => void;
  setActiveTemplate: (id: string | null) => void;
  setFunctionInput: (input: string) => void;
  setIsRunning: (v: boolean) => void;
  setCurrentResult: (result: SandboxExecutionResult) => void;
  selectValidator: (index: number | null) => void;
  clearHistory: () => void;
}

export const useSandboxStore = create<SandboxStore>()(
  persist(
    (set) => ({
      code: "",
      activeTemplateId: null,
      functionInput: "",
      isRunning: false,
      currentResult: null,
      history: [],
      selectedValidatorIndex: null,

      setCode: (code) => set({ code }),
      setActiveTemplate: (id) => set({ activeTemplateId: id }),
      setFunctionInput: (input) => set({ functionInput: input }),
      setIsRunning: (v) => set({ isRunning: v }),
      setCurrentResult: (result) =>
        set((s) => ({
          currentResult: result,
          history: [result, ...s.history].slice(0, 20),
          selectedValidatorIndex: null,
        })),
      selectValidator: (index) => set({ selectedValidatorIndex: index }),
      clearHistory: () => set({ history: [] }),
    }),
    {
      name: "sandbox-store",
      partialize: (s) => ({
        code: s.code,
        activeTemplateId: s.activeTemplateId,
        functionInput: s.functionInput,
      }),
    }
  )
);
