"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { LESSONS } from "@/lib/learn/content";
import { useLearnStore } from "@/store/learnStore";
import { LessonCard } from "@/components/learn/LessonCard";
import { LessonViewer } from "@/components/learn/LessonViewer";
import { Glossary } from "@/components/learn/Glossary";
import { LearningProgress } from "@/components/learn/ProgressBar";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { RotateCcw } from "lucide-react";

const MODULES = [...new Set(LESSONS.map((l) => l.module))];

export default function LearnPage() {
  const { isLessonComplete, getQuizResult, resetProgress, completedLessonIds } = useLearnStore();
  const [activeLessonId, setActiveLessonId] = useState<string | null>(null);
  const [moduleFilter,   setModuleFilter]   = useState<string>("All");

  const activeLesson = LESSONS.find((l) => l.id === activeLessonId) ?? null;

  if (activeLesson) {
    return (
      <div className="min-h-screen bg-[#efece4]">
        <div className="mx-auto max-w-3xl px-6 py-8">
          <LessonViewer lesson={activeLesson} onBack={() => setActiveLessonId(null)} />
        </div>
      </div>
    );
  }

  const filteredLessons = moduleFilter === "All"
    ? LESSONS
    : LESSONS.filter((l) => l.module === moduleFilter);

  return (
    <div className="min-h-screen bg-[#efece4]">
      <div className="mx-auto max-w-7xl px-6 py-8">

        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-[#1a1a1a] tracking-tight mb-2">Learning Center</h1>
          <p className="text-[#6b6560] text-sm max-w-2xl leading-relaxed">
            Master GenLayer, Intelligent Contracts, Optimistic Democracy, and the Equivalence Principle
            through structured lessons, code examples, and interactive quizzes.
          </p>
        </div>

        <Tabs defaultValue="lessons">
          <TabsList className="mb-6">
            <TabsTrigger value="lessons">Lessons</TabsTrigger>
            <TabsTrigger value="glossary">Glossary</TabsTrigger>
            <TabsTrigger value="progress">My Progress</TabsTrigger>
          </TabsList>

          {/* ── Lessons tab ── */}
          <TabsContent value="lessons">
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">

              {/* Sidebar */}
              <div className="lg:col-span-1 space-y-4">
                <LearningProgress />

                {/* Module filter */}
                <div className="rounded-xl border border-[#d8d4c8] bg-white/60 p-4">
                  <p className="text-xs font-semibold text-[#6b6560] uppercase tracking-wider mb-3">Filter by Module</p>
                  <div className="space-y-1">
                    {["All", ...MODULES].map((mod) => (
                      <button key={mod} onClick={() => setModuleFilter(mod)}
                        className={`w-full text-left text-xs px-3 py-2 rounded-lg transition-all ${
                          moduleFilter === mod
                            ? "bg-[#2d2a26] text-[#efece4] font-medium"
                            : "text-[#6b6560] hover:bg-[#e8e4da]"
                        }`}>
                        {mod}
                      </button>
                    ))}
                  </div>
                </div>

                {completedLessonIds.length > 0 && (
                  <Button variant="ghost" size="sm" className="w-full text-xs text-[#6b6560] hover:text-red-500 h-8"
                    onClick={resetProgress}>
                    <RotateCcw className="h-3 w-3 mr-1" /> Reset Progress
                  </Button>
                )}
              </div>

              {/* Lesson grid */}
              <div className="lg:col-span-3">
                <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
                  {filteredLessons.map((lesson, i) => {
                    const qr = getQuizResult(lesson.id);
                    return (
                      <LessonCard
                        key={lesson.id}
                        lesson={lesson}
                        isComplete={isLessonComplete(lesson.id)}
                        quizScore={qr ? qr.score / qr.total : null}
                        onClick={() => setActiveLessonId(lesson.id)}
                        index={i}
                      />
                    );
                  })}
                </div>
              </div>
            </div>
          </TabsContent>

          {/* ── Glossary tab ── */}
          <TabsContent value="glossary">
            <div className="max-w-2xl">
              <Glossary />
            </div>
          </TabsContent>

          {/* ── Progress tab ── */}
          <TabsContent value="progress">
            <div className="max-w-lg space-y-5">
              <LearningProgress />

              <div className="rounded-xl border border-[#d8d4c8] bg-white/60 p-5">
                <p className="text-sm font-semibold text-[#1a1a1a] mb-4">Lesson Completion</p>
                <div className="space-y-2">
                  {LESSONS.map((lesson) => {
                    const done = isLessonComplete(lesson.id);
                    const qr   = getQuizResult(lesson.id);
                    return (
                      <div key={lesson.id} className="flex items-center justify-between py-2 border-b border-[#e8e4da] last:border-0">
                        <div className="flex items-center gap-2">
                          <span className="text-base">{lesson.icon}</span>
                          <div>
                            <p className="text-xs font-medium text-[#1a1a1a]">{lesson.title}</p>
                            <p className="text-[10px] text-[#6b6560]">{lesson.module} · {lesson.xpReward} XP</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2 text-[10px]">
                          {qr && (
                            <span className={qr.score / qr.total >= 0.7 ? "text-green-600 font-semibold" : "text-amber-600"}>
                              Quiz: {Math.round((qr.score / qr.total) * 100)}%
                            </span>
                          )}
                          <span className={done ? "text-green-600 font-semibold" : "text-[#6b6560]"}>
                            {done ? "✓ Done" : "—"}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
