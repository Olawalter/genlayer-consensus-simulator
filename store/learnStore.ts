import { create } from "zustand";
import { persist } from "zustand/middleware";

interface LearnStore {
  completedLessonIds: string[];
  quizResults: Record<string, { score: number; total: number; completedAt: number }>;
  totalXp: number;

  markLessonComplete: (id: string, xpReward: number) => void;
  saveQuizResult: (lessonId: string, score: number, total: number) => void;
  isLessonComplete: (id: string) => boolean;
  getQuizResult: (lessonId: string) => { score: number; total: number; completedAt: number } | null;
  resetProgress: () => void;
}

export const useLearnStore = create<LearnStore>()(
  persist(
    (set, get) => ({
      completedLessonIds: [],
      quizResults: {},
      totalXp: 0,

      markLessonComplete: (id, xpReward) =>
        set((s) => {
          if (s.completedLessonIds.includes(id)) return s;
          return {
            completedLessonIds: [...s.completedLessonIds, id],
            totalXp: s.totalXp + xpReward,
          };
        }),

      saveQuizResult: (lessonId, score, total) =>
        set((s) => ({
          quizResults: { ...s.quizResults, [lessonId]: { score, total, completedAt: Date.now() } },
        })),

      isLessonComplete: (id) => get().completedLessonIds.includes(id),

      getQuizResult: (lessonId) => get().quizResults[lessonId] ?? null,

      resetProgress: () => set({ completedLessonIds: [], quizResults: {}, totalXp: 0 }),
    }),
    { name: "learn-progress-store" }
  )
);
