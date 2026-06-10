"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { ArrowLeft, CheckCircle2, Star, Clock, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { useLearnStore } from "@/store/learnStore";
import { QuizPanel } from "./QuizPanel";
import { QUIZ_QUESTIONS, type Lesson } from "@/lib/learn/content";

interface LessonViewerProps {
  lesson: Lesson;
  onBack: () => void;
}

export function LessonViewer({ lesson, onBack }: LessonViewerProps) {
  const { markLessonComplete, isLessonComplete } = useLearnStore();
  const [showQuiz, setShowQuiz] = useState(false);
  const [readSection, setReadSection] = useState(0);

  const lessonQuestions = QUIZ_QUESTIONS.filter((q) => q.lessonId === lesson.id);
  const isComplete = isLessonComplete(lesson.id);

  function handleSectionComplete() {
    if (readSection < lesson.sections.length - 1) {
      setReadSection(readSection + 1);
    } else if (lessonQuestions.length > 0) {
      setShowQuiz(true);
    } else {
      markLessonComplete(lesson.id, lesson.xpReward);
    }
  }

  if (showQuiz) {
    return (
      <QuizPanel
        lesson={lesson}
        questions={lessonQuestions}
        onComplete={() => {
          markLessonComplete(lesson.id, lesson.xpReward);
          setShowQuiz(false);
        }}
        onBack={() => setShowQuiz(false)}
      />
    );
  }

  const section = lesson.sections[readSection];

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="max-w-2xl mx-auto"
    >
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <Button variant="ghost" size="sm" className="h-8 px-2" onClick={onBack}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-0.5">
            <span className="text-lg">{lesson.icon}</span>
            <h2 className="text-base font-bold text-[#1a1a1a] truncate">{lesson.title}</h2>
            {isComplete && <CheckCircle2 className="h-4 w-4 text-green-500 shrink-0" />}
          </div>
          <div className="flex items-center gap-3 text-[11px] text-[#6b6560]">
            <span className="flex items-center gap-1"><Clock className="h-2.5 w-2.5" />{lesson.estimatedMinutes} min</span>
            <span className="flex items-center gap-1"><Star className="h-2.5 w-2.5 text-amber-400" />{lesson.xpReward} XP</span>
            <Badge variant="secondary" className="text-[9px] px-1.5 py-0">{lesson.module}</Badge>
          </div>
        </div>
      </div>

      {/* Section progress dots */}
      <div className="flex items-center gap-1.5 mb-6">
        {lesson.sections.map((_, i) => (
          <div key={i} className={cn(
            "h-1.5 rounded-full transition-all duration-300",
            i < readSection  ? "bg-[#2d2a26] flex-1" :
            i === readSection ? "bg-[#2d2a26] flex-[2]" :
                                "bg-[#e8e4da] flex-1"
          )} />
        ))}
      </div>

      {/* Section content */}
      <motion.div
        key={readSection}
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-5"
      >
        <h3 className="text-lg font-bold text-[#1a1a1a]">{section.heading}</h3>

        <p className="text-sm text-[#1a1a1a] leading-relaxed whitespace-pre-line">{section.body}</p>

        {section.callout && (
          <div className={cn(
            "rounded-xl border-l-4 px-4 py-3 text-sm leading-relaxed",
            section.callout.type === "info"    && "border-blue-400 bg-blue-50 text-blue-800",
            section.callout.type === "tip"     && "border-green-400 bg-green-50 text-green-800",
            section.callout.type === "warning" && "border-amber-400 bg-amber-50 text-amber-800",
          )}>
            <span className="font-semibold">
              {section.callout.type === "info" ? "ℹ️ " : section.callout.type === "tip" ? "💡 " : "⚠️ "}
            </span>
            {section.callout.text}
          </div>
        )}

        {section.keyPoints && (
          <ul className="space-y-2">
            {section.keyPoints.map((point, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-[#1a1a1a]">
                <span className="h-5 w-5 rounded-full bg-[#2d2a26] text-[#efece4] text-[10px] flex items-center justify-center shrink-0 mt-0.5">
                  {i + 1}
                </span>
                {point}
              </li>
            ))}
          </ul>
        )}

        {section.codeBlock && (
          <div className="rounded-xl bg-[#1a1a1a] overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 bg-[#2d2a26]">
              <span className="text-[11px] text-[#efece4]/60 font-mono">{section.codeBlock.lang}</span>
              <span className="text-[11px] text-[#efece4]/40">Intelligent Contract Example</span>
            </div>
            <pre className="px-4 py-4 text-xs text-[#efece4] overflow-x-auto leading-relaxed font-mono">
              {section.codeBlock.code}
            </pre>
          </div>
        )}
      </motion.div>

      <Separator className="my-6" />

      {/* Navigation */}
      <div className="flex items-center justify-between">
        <span className="text-xs text-[#6b6560]">
          Section {readSection + 1} of {lesson.sections.length}
        </span>
        <Button onClick={handleSectionComplete} className="gap-2">
          {readSection < lesson.sections.length - 1 ? (
            <><ChevronRight className="h-4 w-4" /> Next section</>
          ) : lessonQuestions.length > 0 ? (
            <><Star className="h-4 w-4" /> Take quiz ({lesson.xpReward} XP)</>
          ) : (
            <><CheckCircle2 className="h-4 w-4" /> Complete lesson</>
          )}
        </Button>
      </div>
    </motion.div>
  );
}
