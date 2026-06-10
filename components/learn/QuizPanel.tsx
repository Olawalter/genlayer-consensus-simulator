"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, XCircle, ArrowLeft, Trophy } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { useLearnStore } from "@/store/learnStore";
import type { Lesson, QuizQuestion } from "@/lib/learn/content";

interface QuizPanelProps {
  lesson: Lesson;
  questions: QuizQuestion[];
  onComplete: () => void;
  onBack: () => void;
}

export function QuizPanel({ lesson, questions, onComplete, onBack }: QuizPanelProps) {
  const { saveQuizResult } = useLearnStore();
  const [current, setCurrent]   = useState(0);
  const [answers, setAnswers]   = useState<(number | null)[]>(Array(questions.length).fill(null));
  const [revealed, setRevealed] = useState(false);
  const [finished, setFinished] = useState(false);

  const q = questions[current];
  const selected = answers[current];

  function handleSelect(idx: number) {
    if (revealed) return;
    setAnswers((prev) => { const n = [...prev]; n[current] = idx; return n; });
  }

  function handleReveal() { setRevealed(true); }

  function handleNext() {
    if (current < questions.length - 1) {
      setCurrent(current + 1);
      setRevealed(false);
    } else {
      const score = answers.filter((a, i) => a === questions[i].correctIndex).length;
      saveQuizResult(lesson.id, score, questions.length);
      setFinished(true);
    }
  }

  if (finished) {
    const score = answers.filter((a, i) => a === questions[i].correctIndex).length;
    const pct   = Math.round((score / questions.length) * 100);
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        className="max-w-lg mx-auto text-center py-12"
      >
        <Trophy className={cn("h-14 w-14 mx-auto mb-4", pct >= 70 ? "text-amber-400" : "text-[#d8d4c8]")} />
        <h2 className="text-2xl font-bold text-[#1a1a1a] mb-2">
          {pct >= 90 ? "Excellent!" : pct >= 70 ? "Well done!" : "Keep studying!"}
        </h2>
        <p className="text-4xl font-bold text-[#1a1a1a] my-4">{pct}%</p>
        <p className="text-sm text-[#6b6560] mb-6">
          {score}/{questions.length} correct · {lesson.xpReward} XP earned
        </p>
        <div className="space-y-2">
          {questions.map((q, i) => {
            const correct = answers[i] === q.correctIndex;
            return (
              <div key={q.id} className={cn(
                "flex items-start gap-2 text-left rounded-lg p-3 text-xs",
                correct ? "bg-green-50 border border-green-200" : "bg-red-50 border border-red-200"
              )}>
                {correct ? <CheckCircle2 className="h-3.5 w-3.5 text-green-500 shrink-0 mt-0.5" /> : <XCircle className="h-3.5 w-3.5 text-red-500 shrink-0 mt-0.5" />}
                <div>
                  <p className="font-medium text-[#1a1a1a]">{q.question}</p>
                  {!correct && <p className="text-[#6b6560] mt-0.5">{q.explanation}</p>}
                </div>
              </div>
            );
          })}
        </div>
        <Button className="mt-6 w-full" onClick={onComplete}>
          <CheckCircle2 className="h-4 w-4 mr-2" /> Complete Lesson
        </Button>
      </motion.div>
    );
  }

  return (
    <div className="max-w-lg mx-auto">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <Button variant="ghost" size="sm" className="h-8 px-2" onClick={onBack}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <p className="text-xs font-semibold text-[#6b6560] uppercase tracking-wider">Quiz · {lesson.title}</p>
          <p className="text-xs text-[#6b6560]">Question {current + 1} of {questions.length}</p>
        </div>
      </div>

      {/* Progress */}
      <div className="flex gap-1 mb-6">
        {questions.map((_, i) => (
          <div key={i} className={cn("h-1 flex-1 rounded-full", i < current ? "bg-[#2d2a26]" : i === current ? "bg-[#2d2a26]/50" : "bg-[#e8e4da]")} />
        ))}
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={current}
          initial={{ opacity: 0, x: 16 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -16 }}
          className="space-y-5"
        >
          <h3 className="text-base font-semibold text-[#1a1a1a] leading-relaxed">{q.question}</h3>

          <div className="space-y-2">
            {q.options.map((opt, i) => {
              const isSelected = selected === i;
              const isCorrect  = i === q.correctIndex;
              return (
                <button key={i} onClick={() => handleSelect(i)}
                  className={cn(
                    "w-full text-left rounded-xl border-2 px-4 py-3 text-sm transition-all",
                    !revealed && isSelected && "border-[#2d2a26] bg-[#2d2a26] text-[#efece4]",
                    !revealed && !isSelected && "border-[#d8d4c8] bg-white/60 hover:border-[#b8b4a8]",
                    revealed  && isCorrect  && "border-green-400 bg-green-50 text-green-800",
                    revealed  && isSelected && !isCorrect && "border-red-400 bg-red-50 text-red-800",
                    revealed  && !isSelected && !isCorrect && "border-[#e8e4da] bg-white/30 text-[#6b6560]",
                  )}
                >
                  <span className="font-medium mr-2">{String.fromCharCode(65 + i)}.</span>
                  {opt}
                </button>
              );
            })}
          </div>

          {revealed && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              className="rounded-xl border border-blue-200 bg-blue-50 p-4 text-xs text-blue-800 leading-relaxed"
            >
              <span className="font-semibold">Explanation: </span>{q.explanation}
            </motion.div>
          )}

          <div className="flex gap-2">
            {selected !== null && !revealed && (
              <Button variant="outline" className="flex-1" onClick={handleReveal}>Check Answer</Button>
            )}
            {revealed && (
              <Button className="flex-1" onClick={handleNext}>
                {current < questions.length - 1 ? "Next Question" : "See Results"}
              </Button>
            )}
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
