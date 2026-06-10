"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { CONTRACT_TEMPLATES, type ContractTemplate } from "@/lib/sandbox/templates";

interface TemplateSelectorProps {
  activeId: string | null;
  onSelect: (t: ContractTemplate) => void;
}

const CATEGORY_COLORS: Record<string, string> = {
  Finance:    "bg-green-100 text-green-700",
  Oracle:     "bg-blue-100 text-blue-700",
  Governance: "bg-purple-100 text-purple-700",
  Social:     "bg-amber-100 text-amber-700",
};

const DIFF_COLORS: Record<string, string> = {
  beginner:     "text-green-600",
  intermediate: "text-amber-600",
  advanced:     "text-red-600",
};

export function TemplateSelector({ activeId, onSelect }: TemplateSelectorProps) {
  return (
    <div className="space-y-1.5">
      <p className="text-[11px] font-semibold text-[#6b6560] uppercase tracking-wider mb-2">
        Contract Templates
      </p>
      {CONTRACT_TEMPLATES.map((t, i) => (
        <motion.button
          key={t.id}
          initial={{ opacity: 0, x: -8 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: i * 0.05 }}
          onClick={() => onSelect(t)}
          className={cn(
            "w-full text-left rounded-lg border px-3 py-2.5 transition-all duration-150 group",
            activeId === t.id
              ? "border-[#2d2a26] bg-[#2d2a26] text-white"
              : "border-[#e8e4da] bg-white/60 hover:border-[#b8b4a8] hover:bg-white/80"
          )}
        >
          <div className="flex items-center gap-2 mb-0.5">
            <span className="text-base leading-none">{t.icon}</span>
            <span className={cn(
              "text-xs font-semibold truncate",
              activeId === t.id ? "text-white" : "text-[#1a1a1a]"
            )}>
              {t.name}
            </span>
          </div>
          <div className="flex items-center gap-1.5 mt-1">
            <span className={cn(
              "text-[9px] font-semibold px-1.5 py-0.5 rounded-full",
              activeId === t.id ? "bg-white/20 text-white" : CATEGORY_COLORS[t.category]
            )}>
              {t.category}
            </span>
            <span className={cn(
              "text-[9px] font-medium capitalize",
              activeId === t.id ? "text-white/60" : DIFF_COLORS[t.difficulty]
            )}>
              {t.difficulty}
            </span>
          </div>
        </motion.button>
      ))}
    </div>
  );
}
