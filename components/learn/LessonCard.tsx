"use client";

import { motion } from "framer-motion";
import { Clock, Star, CheckCircle2, Lock } from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import type { Lesson, Difficulty } from "@/lib/learn/content";

interface LessonCardProps {
  lesson: Lesson;
  isComplete: boolean;
  quizScore: number | null;
  isLocked?: boolean;
  onClick: () => void;
  index: number;
}

const DIFF_CFG: Record<Difficulty, { label: string; cls: string }> = {
  beginner:     { label: "Beginner",     cls: "bg-green-100 text-green-700" },
  intermediate: { label: "Intermediate", cls: "bg-amber-100 text-amber-700" },
  advanced:     { label: "Advanced",     cls: "bg-red-100 text-red-700" },
};

export function LessonCard({ lesson, isComplete, quizScore, isLocked, onClick, index }: LessonCardProps) {
  const diff = DIFF_CFG[lesson.difficulty];

  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.06 }}
      onClick={!isLocked ? onClick : undefined}
      className={cn(
        "rounded-xl border-2 p-5 transition-all duration-200",
        isLocked  ? "border-[#e8e4da] bg-white/30 opacity-60 cursor-not-allowed" :
        isComplete ? "border-green-200 bg-green-50/50 cursor-pointer hover:shadow-md" :
                    "border-[#d8d4c8] bg-white/60 cursor-pointer hover:border-[#b8b4a8] hover:shadow-sm"
      )}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <span className="text-2xl">{lesson.icon}</span>
          <div>
            <h3 className="text-sm font-bold text-[#1a1a1a] leading-tight">{lesson.title}</h3>
            <p className="text-xs text-[#6b6560] mt-0.5">{lesson.subtitle}</p>
          </div>
        </div>
        <div className="flex flex-col items-end gap-1.5 shrink-0 ml-2">
          {isLocked    && <Lock className="h-4 w-4 text-[#d8d4c8]" />}
          {isComplete  && <CheckCircle2 className="h-5 w-5 text-green-500" />}
        </div>
      </div>

      {/* Badges */}
      <div className="flex items-center gap-2 flex-wrap mb-3">
        <span className={cn("text-[10px] font-semibold px-2 py-0.5 rounded-full", diff.cls)}>
          {diff.label}
        </span>
        <span className="text-[10px] text-[#6b6560] flex items-center gap-1">
          <Clock className="h-2.5 w-2.5" /> {lesson.estimatedMinutes} min
        </span>
        <span className="text-[10px] text-[#6b6560] flex items-center gap-1">
          <Star className="h-2.5 w-2.5 text-amber-400" /> {lesson.xpReward} XP
        </span>
        <Badge variant="secondary" className="text-[9px] px-1.5 py-0">{lesson.module}</Badge>
      </div>

      {/* Quiz score */}
      {quizScore !== null && (
        <div className="mt-2 pt-2 border-t border-[#e8e4da]">
          <p className="text-[10px] text-[#6b6560]">
            Quiz: <span className={cn("font-semibold", quizScore >= 0.7 ? "text-green-600" : "text-amber-600")}>
              {Math.round(quizScore * 100)}%
            </span>
          </p>
        </div>
      )}
    </motion.div>
  );
}
