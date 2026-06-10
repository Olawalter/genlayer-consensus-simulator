"use client";

import { motion } from "framer-motion";
import { Star, BookOpen, Trophy } from "lucide-react";
import { LESSONS } from "@/lib/learn/content";
import { useLearnStore } from "@/store/learnStore";

export function LearningProgress() {
  const { completedLessonIds, totalXp, quizResults } = useLearnStore();
  const total     = LESSONS.length;
  const completed = completedLessonIds.length;
  const pct       = Math.round((completed / total) * 100);
  const quizCount = Object.keys(quizResults).length;

  const maxXp = LESSONS.reduce((s, l) => s + l.xpReward, 0);
  const level  = Math.floor(totalXp / 100) + 1;

  return (
    <div className="rounded-xl border border-[#d8d4c8] bg-white/60 p-5">
      <div className="flex items-center justify-between mb-4">
        <div>
          <p className="text-sm font-bold text-[#1a1a1a]">Your Progress</p>
          <p className="text-xs text-[#6b6560]">Level {level} learner</p>
        </div>
        <div className="flex items-center gap-1.5 bg-amber-50 border border-amber-200 rounded-full px-3 py-1">
          <Star className="h-3.5 w-3.5 text-amber-500" />
          <span className="text-xs font-bold text-amber-700">{totalXp} XP</span>
        </div>
      </div>

      {/* Overall progress */}
      <div className="mb-4">
        <div className="flex justify-between text-xs text-[#6b6560] mb-1.5">
          <span>Lessons completed</span>
          <span className="font-semibold text-[#1a1a1a]">{completed}/{total}</span>
        </div>
        <div className="h-3 rounded-full bg-[#e8e4da] overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${pct}%` }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="h-full rounded-full bg-[#2d2a26]"
          />
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-3 text-center">
        {[
          { icon: BookOpen, label: "Completed",    value: completed },
          { icon: Star,     label: "Quizzes done", value: quizCount },
          { icon: Trophy,   label: "Total XP",     value: totalXp },
        ].map((s) => (
          <div key={s.label} className="rounded-lg bg-[#f5f2ec] p-2.5">
            <s.icon className="h-4 w-4 text-[#6b6560] mx-auto mb-1" />
            <p className="text-sm font-bold text-[#1a1a1a]">{s.value}</p>
            <p className="text-[10px] text-[#6b6560]">{s.label}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
