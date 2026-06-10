import { create } from "zustand";
import type { SimulationRun, SimulationStatus } from "@/services/simulationService";

interface SimulationStore {
  currentRun: SimulationRun | null;
  history: SimulationRun[];
  isRunning: boolean;
  error: string | null;

  setCurrentRun: (run: SimulationRun) => void;
  clearCurrentRun: () => void;
  setError: (error: string | null) => void;
  addToHistory: (run: SimulationRun) => void;
}

export const useSimulationStore = create<SimulationStore>((set) => ({
  currentRun: null,
  history: [],
  isRunning: false,
  error: null,

  setCurrentRun: (run) =>
    set({
      currentRun: run,
      isRunning: ["submitting", "running", "computing", "appealing"].includes(run.status as SimulationStatus),
    }),

  clearCurrentRun: () => set({ currentRun: null, isRunning: false, error: null }),

  setError: (error) => set({ error }),

  addToHistory: (run) =>
    set((state) => ({
      history: [run, ...state.history].slice(0, 20), // keep last 20
    })),
}));
