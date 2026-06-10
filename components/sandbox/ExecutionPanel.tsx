"use client";

import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import type { SandboxExecutionResult, ValidatorExecution } from "@/lib/sandbox/executor";
import { CheckCircle2, XCircle, AlertCircle, Zap, Clock } from "lucide-react";
import { useSandboxStore } from "@/store/sandboxStore";

const VOTE_CONFIG = {
  ACCEPT:    { cls: "bg-green-100 text-green-700 border-green-200",  icon: CheckCircle2, dot: "bg-green-500" },
  REJECT:    { cls: "bg-red-100 text-red-700 border-red-200",        icon: XCircle,      dot: "bg-red-500" },
  UNCERTAIN: { cls: "bg-amber-100 text-amber-700 border-amber-200",  icon: AlertCircle,  dot: "bg-amber-500" },
};

const OUTCOME_CONFIG = {
  ACCEPTED: { cls: "border-green-300 bg-green-50",  label: "ACCEPTED",       icon: "✅" },
  REJECTED: { cls: "border-red-300 bg-red-50",      label: "REJECTED",       icon: "❌" },
  SPLIT:    { cls: "border-amber-300 bg-amber-50",   label: "SPLIT / APPEAL", icon: "⚡" },
};

interface ValidatorCardProps {
  v: ValidatorExecution;
  isSelected: boolean;
  onClick: () => void;
  index: number;
}

function ValidatorCard({ v, isSelected, onClick, index }: ValidatorCardProps) {
  const cfg = VOTE_CONFIG[v.vote];
  const Icon = cfg.icon;
  return (
    <motion.button
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.07 }}
      onClick={onClick}
      className={cn(
        "w-full text-left rounded-xl border-2 p-3 transition-all duration-200",
        isSelected ? "border-[#2d2a26] shadow-md" : "border-[#e8e4da] hover:border-[#b8b4a8]",
        "bg-white/70"
      )}
    >
      <div className="flex items-start justify-between gap-2 mb-2">
        <div>
          <p className="text-xs font-bold text-[#1a1a1a] leading-tight">{v.validatorName}</p>
          <p className="text-[10px] text-[#6b6560]">{v.llmModel}</p>
        </div>
        <div className={cn("flex items-center gap-1 px-2 py-0.5 rounded-full border text-[10px] font-bold shrink-0", cfg.cls)}>
          <Icon className="h-3 w-3" />
          {v.vote}
        </div>
      </div>
      <div className="flex items-center gap-2">
        <div className="flex-1 h-1.5 bg-[#e8e4da] rounded-full overflow-hidden">
          <div
            className={cn("h-full rounded-full transition-all", cfg.dot)}
            style={{ width: `${Math.round(v.confidence * 100)}%` }}
          />
        </div>
        <span className="text-[10px] text-[#6b6560] shrink-0">{Math.round(v.confidence * 100)}%</span>
      </div>
      <div className="flex items-center gap-3 mt-2 text-[10px] text-[#6b6560]">
        <span className="flex items-center gap-0.5"><Clock className="h-2.5 w-2.5" />{v.executionMs}ms</span>
        <span className="flex items-center gap-0.5"><Zap className="h-2.5 w-2.5" />{v.llmProvider}</span>
      </div>
    </motion.button>
  );
}

interface ExecutionPanelProps {
  result: SandboxExecutionResult;
}

export function ExecutionPanel({ result }: ExecutionPanelProps) {
  const { selectedValidatorIndex, selectValidator } = useSandboxStore();
  const selected = selectedValidatorIndex !== null ? result.validators[selectedValidatorIndex] : null;
  const outCfg = OUTCOME_CONFIG[result.finalOutcome];

  return (
    <div className="space-y-4 h-full overflow-y-auto pr-1">
      {/* Final outcome banner */}
      <motion.div
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        className={cn("rounded-xl border-2 px-4 py-3 flex items-center justify-between", outCfg.cls)}
      >
        <div>
          <p className="text-xs font-bold text-[#1a1a1a]">
            {outCfg.icon} {outCfg.label}
          </p>
          <p className="text-[11px] text-[#6b6560] mt-0.5">
            {result.contractName}.{result.functionCalled}("{result.input.slice(0, 40)}{result.input.length > 40 ? "…" : ""}")
          </p>
        </div>
        <div className="text-right shrink-0">
          <p className="text-[10px] text-[#6b6560]">{result.totalMs}ms total</p>
          <p className="text-[10px] text-[#6b6560]">{result.validators.length} validators</p>
        </div>
      </motion.div>

      {/* Equivalence result */}
      <div className="rounded-xl border border-[#d8d4c8] bg-white/60 px-4 py-3">
        <p className="text-[11px] font-semibold text-[#6b6560] uppercase tracking-wider mb-1.5">Equivalence Check</p>
        <div className="flex items-center gap-2 mb-2">
          <div className="flex-1 h-2 bg-[#e8e4da] rounded-full overflow-hidden">
            <div
              className={cn("h-full rounded-full", result.equivalence.passed ? "bg-green-500" : "bg-amber-500")}
              style={{ width: `${Math.round(result.equivalence.agreeingCount / result.equivalence.totalCount * 100)}%` }}
            />
          </div>
          <span className="text-xs font-bold text-[#1a1a1a]">
            {Math.round(result.equivalence.agreeingCount / result.equivalence.totalCount * 100)}%
          </span>
          <span className={cn("text-[10px] font-bold px-2 py-0.5 rounded-full", result.equivalence.passed ? "bg-green-100 text-green-700" : "bg-amber-100 text-amber-700")}>
            {result.equivalence.passed ? "PASSED" : "FAILED"}
          </span>
        </div>
        {/* 60% threshold marker */}
        <div className="relative h-0 mb-1">
          <div className="absolute left-[60%] -translate-x-1/2 -top-5 text-[9px] text-[#6b6560]">60%</div>
          <div className="absolute left-[60%] -translate-x-1/2 -top-3 w-px h-3 bg-[#6b6560]/40" />
        </div>
        <p className="text-[11px] text-[#6b6560] leading-snug mt-1">{result.equivalence.explanation}</p>
      </div>

      {/* Validator cards grid */}
      <div>
        <p className="text-[11px] font-semibold text-[#6b6560] uppercase tracking-wider mb-2">Validator Votes</p>
        <div className="grid grid-cols-1 gap-2">
          {result.validators.map((v, i) => (
            <ValidatorCard
              key={i}
              v={v}
              index={i}
              isSelected={selectedValidatorIndex === i}
              onClick={() => selectValidator(selectedValidatorIndex === i ? null : i)}
            />
          ))}
        </div>
      </div>

      {/* Selected validator detail */}
      <AnimatePresence>
        {selected && (
          <motion.div
            key={selected.validatorIndex}
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <div className="rounded-xl border-2 border-[#2d2a26] bg-[#1a1a1a] p-4 space-y-3">
              <p className="text-xs font-bold text-[#efece4]">{selected.validatorName} — Detail</p>

              <div>
                <p className="text-[10px] text-[#5a5550] mb-1 font-mono">PROMPT SENT</p>
                <p className="text-[11px] text-[#d8d4c8] font-mono leading-snug bg-[#2d2a26] rounded px-2 py-2">
                  {selected.promptSent}
                </p>
              </div>

              <div>
                <p className="text-[10px] text-[#5a5550] mb-1 font-mono">LLM RESPONSE</p>
                <p className="text-xs text-green-400 font-mono">{selected.llmResponse}</p>
              </div>

              <div>
                <p className="text-[10px] text-[#5a5550] mb-1 font-mono">REASONING</p>
                <p className="text-[11px] text-[#c8c4bc] leading-snug">{selected.reasoning}</p>
              </div>

              {Object.keys(selected.stateAfter).length > 0 && (
                <div>
                  <p className="text-[10px] text-[#5a5550] mb-1 font-mono">STATE AFTER</p>
                  <div className="space-y-1">
                    {Object.entries(selected.stateAfter).map(([k, v]) => (
                      <div key={k} className="flex items-center gap-2 text-[11px] font-mono">
                        <span className="text-[#8080ff]">{k}</span>
                        <span className="text-[#5a5550]">=</span>
                        <span className="text-[#d8d4c8]">{v}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
