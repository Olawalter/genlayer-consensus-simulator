"use client";

import { motion } from "framer-motion";
import { CheckCircle2, XCircle, HelpCircle, BarChart2, Cpu, Sliders, RotateCcw } from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { PERSONA_COLORS } from "@/lib/validators/personas";
import type { CustomValidator } from "@/store/validatorStore";

interface ValidatorProfileProps {
  validator: CustomValidator;
  isSelected: boolean;
  isInComparison: boolean;
  onSelect: () => void;
  onToggleComparison: () => void;
  onEdit: () => void;
  onReset: () => void;
}

export function ValidatorProfile({
  validator, isSelected, isInComparison, onSelect, onToggleComparison, onEdit, onReset,
}: ValidatorProfileProps) {
  const colors = PERSONA_COLORS[validator.color] ?? PERSONA_COLORS.indigo;
  const hasHistory = validator.totalVotes > 0;

  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.97 }}
      animate={{ opacity: 1, scale: 1 }}
      className={cn(
        "rounded-xl border-2 bg-white/70 backdrop-blur-sm p-5 cursor-pointer transition-all duration-200",
        isSelected ? "border-[#2d2a26] shadow-lg" : "border-[#d8d4c8] hover:border-[#b8b4a8]"
      )}
      onClick={onSelect}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={cn("h-11 w-11 rounded-xl flex items-center justify-center text-sm font-bold shrink-0", colors.bg, colors.text)}>
            {validator.avatar}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-[#1a1a1a]">{validator.name}</h3>
              {validator.isCustom && (
                <Badge variant="secondary" className="text-[10px] px-1.5 py-0">modified</Badge>
              )}
            </div>
            <p className="text-xs text-[#6b6560] flex items-center gap-1 mt-0.5">
              <Cpu className="h-2.5 w-2.5" /> {validator.model}
            </p>
            <p className="text-[11px] text-[#6b6560] capitalize mt-0.5">{validator.persona} persona</p>
          </div>
        </div>
        <div className="flex flex-col gap-1" onClick={(e) => e.stopPropagation()}>
          <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={onEdit}>
            <Sliders className="h-3.5 w-3.5" />
          </Button>
          {validator.isCustom && (
            <Button variant="ghost" size="sm" className="h-7 w-7 p-0 text-[#6b6560] hover:text-red-500" onClick={onReset}>
              <RotateCcw className="h-3.5 w-3.5" />
            </Button>
          )}
        </div>
      </div>

      <p className="text-xs text-[#6b6560] leading-relaxed mb-4">{validator.description}</p>

      <Separator className="mb-4" />

      {/* Bias sliders — read-only display */}
      <div className="space-y-2.5 mb-4">
        <div>
          <div className="flex justify-between text-[11px] text-[#6b6560] mb-1">
            <span>Accept Threshold</span>
            <span className="font-medium text-[#1a1a1a]">{Math.round(validator.acceptThreshold * 100)}%</span>
          </div>
          <Progress value={Math.round(validator.acceptThreshold * 100)} className="h-1.5" />
        </div>
        <div>
          <div className="flex justify-between text-[11px] text-[#6b6560] mb-1">
            <span>Base Confidence</span>
            <span className="font-medium text-[#1a1a1a]">{Math.round(validator.confidenceBase * 100)}%</span>
          </div>
          <Progress value={Math.round(validator.confidenceBase * 100)} className="h-1.5" />
        </div>
        <div>
          <div className="flex justify-between text-[11px] text-[#6b6560] mb-1">
            <span>Uncertainty Range</span>
            <span className="font-medium text-[#1a1a1a]">{Math.round(validator.uncertaintyRange * 100)}%</span>
          </div>
          <Progress value={Math.round(validator.uncertaintyRange * 100)} className="h-1.5" />
        </div>
      </div>

      {/* Stats */}
      {hasHistory && (
        <>
          <Separator className="mb-4" />
          <div className="grid grid-cols-3 gap-2 mb-4">
            <div className="text-center">
              <div className="flex items-center justify-center gap-1 text-green-600 mb-0.5">
                <CheckCircle2 className="h-3 w-3" />
                <span className="text-xs font-semibold">{Math.round(validator.acceptRate * 100)}%</span>
              </div>
              <p className="text-[10px] text-[#6b6560]">Accept</p>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center gap-1 text-red-600 mb-0.5">
                <XCircle className="h-3 w-3" />
                <span className="text-xs font-semibold">{Math.round(validator.rejectRate * 100)}%</span>
              </div>
              <p className="text-[10px] text-[#6b6560]">Reject</p>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center gap-1 text-amber-600 mb-0.5">
                <HelpCircle className="h-3 w-3" />
                <span className="text-xs font-semibold">{Math.round(validator.uncertainRate * 100)}%</span>
              </div>
              <p className="text-[10px] text-[#6b6560]">Uncertain</p>
            </div>
          </div>
          <div className="flex items-center gap-1.5 text-[11px] text-[#6b6560]">
            <BarChart2 className="h-3 w-3" />
            <span>{validator.totalVotes} votes · avg confidence {Math.round(validator.avgConfidence * 100)}%</span>
          </div>
        </>
      )}

      {!hasHistory && (
        <p className="text-[11px] text-[#6b6560] italic">No vote history yet. Run a simulation to see stats.</p>
      )}

      {/* Comparison toggle */}
      <div className="mt-4 pt-4 border-t border-[#e8e4da]" onClick={(e) => e.stopPropagation()}>
        <Button
          variant={isInComparison ? "default" : "outline"}
          size="sm"
          className="w-full text-xs h-8"
          onClick={onToggleComparison}
        >
          {isInComparison ? "✓ In Comparison" : "Add to Comparison"}
        </Button>
      </div>
    </motion.div>
  );
}
