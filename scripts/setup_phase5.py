"""Phase 5: Validator Lab — persona editor, bias controls, vote history, comparison mode."""
import pathlib

ROOT = pathlib.Path("C:/GenB/GenLayer Consensus Simulator")


def w(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"  WROTE  {rel}")


# ─────────────────────────────────────────────────────────────────────────────
# 1. Validator store (Zustand) — manages custom validator configurations
# ─────────────────────────────────────────────────────────────────────────────
w("store/validatorStore.ts", '''\
import { create } from "zustand";
import { persist } from "zustand/middleware";
import { VALIDATOR_PERSONAS, type ValidatorPersonaConfig } from "@/lib/validators/personas";

export interface CustomValidator extends ValidatorPersonaConfig {
  id: string;
  isCustom: boolean;
  createdAt: number;
  voteHistory: VoteRecord[];
  totalVotes: number;
  acceptRate: number;
  rejectRate: number;
  uncertainRate: number;
  avgConfidence: number;
}

export interface VoteRecord {
  id: string;
  claim: string;
  category: string;
  vote: "ACCEPT" | "REJECT" | "UNCERTAIN";
  confidence: number;
  reasoning: string;
  simulationId: string;
  timestamp: number;
}

interface ValidatorStore {
  validators: CustomValidator[];
  selectedValidatorId: string | null;
  comparisonIds: string[];

  selectValidator: (id: string) => void;
  toggleComparison: (id: string) => void;
  clearComparison: () => void;
  updateValidator: (id: string, patch: Partial<ValidatorPersonaConfig>) => void;
  resetValidator: (id: string) => void;
  addVoteRecord: (validatorId: string, record: Omit<VoteRecord, "id" | "timestamp">) => void;
  clearHistory: (validatorId: string) => void;
}

function seedValidators(): CustomValidator[] {
  return VALIDATOR_PERSONAS.map((p, i) => ({
    ...p,
    id: `default_${i}`,
    isCustom: false,
    createdAt: Date.now(),
    voteHistory: [],
    totalVotes: 0,
    acceptRate: 0,
    rejectRate: 0,
    uncertainRate: 0,
    avgConfidence: p.confidenceBase,
  }));
}

function recomputeStats(v: CustomValidator): CustomValidator {
  const h = v.voteHistory;
  if (h.length === 0) return { ...v, totalVotes: 0, acceptRate: 0, rejectRate: 0, uncertainRate: 0, avgConfidence: v.confidenceBase };
  const total = h.length;
  const accept    = h.filter((r) => r.vote === "ACCEPT").length;
  const reject    = h.filter((r) => r.vote === "REJECT").length;
  const uncertain = h.filter((r) => r.vote === "UNCERTAIN").length;
  const avgConf   = h.reduce((s, r) => s + r.confidence, 0) / total;
  return {
    ...v,
    totalVotes:    total,
    acceptRate:    accept    / total,
    rejectRate:    reject    / total,
    uncertainRate: uncertain / total,
    avgConfidence: avgConf,
  };
}

export const useValidatorStore = create<ValidatorStore>()(
  persist(
    (set) => ({
      validators: seedValidators(),
      selectedValidatorId: null,
      comparisonIds: [],

      selectValidator: (id) => set({ selectedValidatorId: id }),

      toggleComparison: (id) =>
        set((state) => {
          const already = state.comparisonIds.includes(id);
          if (already) return { comparisonIds: state.comparisonIds.filter((x) => x !== id) };
          if (state.comparisonIds.length >= 3) return state; // max 3 at once
          return { comparisonIds: [...state.comparisonIds, id] };
        }),

      clearComparison: () => set({ comparisonIds: [] }),

      updateValidator: (id, patch) =>
        set((state) => ({
          validators: state.validators.map((v) =>
            v.id === id ? { ...v, ...patch, isCustom: true } : v
          ),
        })),

      resetValidator: (id) =>
        set((state) => {
          const idx = state.validators.findIndex((v) => v.id === id);
          if (idx === -1) return state;
          const defaultIdx = parseInt(id.replace("default_", ""), 10);
          const original = VALIDATOR_PERSONAS[defaultIdx] ?? VALIDATOR_PERSONAS[0];
          return {
            validators: state.validators.map((v) =>
              v.id === id ? { ...v, ...original, isCustom: false } : v
            ),
          };
        }),

      addVoteRecord: (validatorId, record) =>
        set((state) => ({
          validators: state.validators.map((v) => {
            if (v.id !== validatorId) return v;
            const newRecord: VoteRecord = { ...record, id: `vr_${Date.now()}`, timestamp: Date.now() };
            const updated: CustomValidator = { ...v, voteHistory: [newRecord, ...v.voteHistory].slice(0, 50) };
            return recomputeStats(updated);
          }),
        })),

      clearHistory: (validatorId) =>
        set((state) => ({
          validators: state.validators.map((v) =>
            v.id === validatorId ? recomputeStats({ ...v, voteHistory: [] }) : v
          ),
        })),
    }),
    {
      name: "validator-lab-store",
      partialize: (s) => ({ validators: s.validators }),
    }
  )
);
''')

# ─────────────────────────────────────────────────────────────────────────────
# 2. UI: Slider component
# ─────────────────────────────────────────────────────────────────────────────
w("components/ui/slider.tsx", '''\
"use client";
import * as React from "react";
import * as SliderPrimitive from "@radix-ui/react-slider";
import { cn } from "@/lib/utils";

const Slider = React.forwardRef<
  React.ElementRef<typeof SliderPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof SliderPrimitive.Root>
>(({ className, ...props }, ref) => (
  <SliderPrimitive.Root
    ref={ref}
    className={cn("relative flex w-full touch-none select-none items-center", className)}
    {...props}
  >
    <SliderPrimitive.Track className="relative h-2 w-full grow overflow-hidden rounded-full bg-[#e8e4da]">
      <SliderPrimitive.Range className="absolute h-full bg-[#2d2a26]" />
    </SliderPrimitive.Track>
    <SliderPrimitive.Thumb className="block h-4 w-4 rounded-full border-2 border-[#2d2a26] bg-white ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 cursor-grab active:cursor-grabbing" />
  </SliderPrimitive.Root>
));
Slider.displayName = SliderPrimitive.Root.displayName;

export { Slider };
''')

# ─────────────────────────────────────────────────────────────────────────────
# 3. UI: Tabs component
# ─────────────────────────────────────────────────────────────────────────────
w("components/ui/tabs.tsx", '''\
"use client";
import * as React from "react";
import * as TabsPrimitive from "@radix-ui/react-tabs";
import { cn } from "@/lib/utils";

const Tabs = TabsPrimitive.Root;

const TabsList = React.forwardRef<
  React.ElementRef<typeof TabsPrimitive.List>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitive.List>
>(({ className, ...props }, ref) => (
  <TabsPrimitive.List
    ref={ref}
    className={cn(
      "inline-flex h-10 items-center justify-center rounded-lg bg-[#e8e4da] p-1 text-[#6b6560]",
      className
    )}
    {...props}
  />
));
TabsList.displayName = TabsPrimitive.List.displayName;

const TabsTrigger = React.forwardRef<
  React.ElementRef<typeof TabsPrimitive.Trigger>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitive.Trigger>
>(({ className, ...props }, ref) => (
  <TabsPrimitive.Trigger
    ref={ref}
    className={cn(
      "inline-flex items-center justify-center whitespace-nowrap rounded-md px-3 py-1.5 text-sm font-medium",
      "ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
      "disabled:pointer-events-none disabled:opacity-50",
      "data-[state=active]:bg-white data-[state=active]:text-[#1a1a1a] data-[state=active]:shadow-sm",
      className
    )}
    {...props}
  />
));
TabsTrigger.displayName = TabsPrimitive.Trigger.displayName;

const TabsContent = React.forwardRef<
  React.ElementRef<typeof TabsPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitive.Content>
>(({ className, ...props }, ref) => (
  <TabsPrimitive.Content
    ref={ref}
    className={cn("mt-4 ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2", className)}
    {...props}
  />
));
TabsContent.displayName = TabsPrimitive.Content.displayName;

export { Tabs, TabsList, TabsTrigger, TabsContent };
''')

# ─────────────────────────────────────────────────────────────────────────────
# 4. UI: Separator
# ─────────────────────────────────────────────────────────────────────────────
w("components/ui/separator.tsx", '''\
"use client";
import * as React from "react";
import * as SeparatorPrimitive from "@radix-ui/react-separator";
import { cn } from "@/lib/utils";

const Separator = React.forwardRef<
  React.ElementRef<typeof SeparatorPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof SeparatorPrimitive.Root>
>(({ className, orientation = "horizontal", decorative = true, ...props }, ref) => (
  <SeparatorPrimitive.Root
    ref={ref}
    decorative={decorative}
    orientation={orientation}
    className={cn(
      "shrink-0 bg-[#e8e4da]",
      orientation === "horizontal" ? "h-[1px] w-full" : "h-full w-[1px]",
      className
    )}
    {...props}
  />
));
Separator.displayName = SeparatorPrimitive.Root.displayName;

export { Separator };
''')

# ─────────────────────────────────────────────────────────────────────────────
# 5. UI: Tooltip
# ─────────────────────────────────────────────────────────────────────────────
w("components/ui/tooltip.tsx", '''\
"use client";
import * as React from "react";
import * as TooltipPrimitive from "@radix-ui/react-tooltip";
import { cn } from "@/lib/utils";

const TooltipProvider = TooltipPrimitive.Provider;
const Tooltip = TooltipPrimitive.Root;
const TooltipTrigger = TooltipPrimitive.Trigger;

const TooltipContent = React.forwardRef<
  React.ElementRef<typeof TooltipPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof TooltipPrimitive.Content>
>(({ className, sideOffset = 4, ...props }, ref) => (
  <TooltipPrimitive.Portal>
    <TooltipPrimitive.Content
      ref={ref}
      sideOffset={sideOffset}
      className={cn(
        "z-50 overflow-hidden rounded-md border border-[#d8d4c8] bg-white px-3 py-1.5 text-xs text-[#1a1a1a] shadow-md",
        "animate-fade-up",
        className
      )}
      {...props}
    />
  </TooltipPrimitive.Portal>
));
TooltipContent.displayName = TooltipPrimitive.Content.displayName;

export { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider };
''')

# ─────────────────────────────────────────────────────────────────────────────
# 6. Validator Profile Card (full detail)
# ─────────────────────────────────────────────────────────────────────────────
w("components/validators/ValidatorProfile.tsx", '''\
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
''')

# ─────────────────────────────────────────────────────────────────────────────
# 7. Bias Editor (side panel)
# ─────────────────────────────────────────────────────────────────────────────
w("components/validators/BiasEditor.tsx", '''\
"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Info } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { Separator } from "@/components/ui/separator";
import { Tooltip, TooltipContent, TooltipTrigger, TooltipProvider } from "@/components/ui/tooltip";
import { PERSONA_COLORS } from "@/lib/validators/personas";
import { useValidatorStore, type CustomValidator } from "@/store/validatorStore";

interface BiasEditorProps {
  validator: CustomValidator | null;
  onClose: () => void;
}

interface SliderField {
  key: keyof Pick<CustomValidator, "acceptThreshold" | "uncertaintyRange" | "confidenceBase">;
  label: string;
  description: string;
  min: number;
  max: number;
  step: number;
  format: (v: number) => string;
}

const FIELDS: SliderField[] = [
  {
    key: "acceptThreshold",
    label: "Accept Threshold",
    description: "The probability level at which this validator tends to accept a claim. Higher = more lenient.",
    min: 0.1, max: 0.9, step: 0.01,
    format: (v) => `${Math.round(v * 100)}%`,
  },
  {
    key: "uncertaintyRange",
    label: "Uncertainty Range",
    description: "The width of the zone around the threshold where the validator reports UNCERTAIN instead of a definitive vote.",
    min: 0.05, max: 0.4, step: 0.01,
    format: (v) => `±${Math.round(v * 100 / 2)}%`,
  },
  {
    key: "confidenceBase",
    label: "Base Confidence",
    description: "The baseline confidence level for this validator's votes. Higher confidence validators have more influence in equivalence scoring.",
    min: 0.5, max: 0.99, step: 0.01,
    format: (v) => `${Math.round(v * 100)}%`,
  },
];

export function BiasEditor({ validator, onClose }: BiasEditorProps) {
  const { updateValidator } = useValidatorStore();
  const [local, setLocal] = useState<Record<string, number>>({});

  useEffect(() => {
    if (validator) {
      setLocal({
        acceptThreshold:  validator.acceptThreshold,
        uncertaintyRange: validator.uncertaintyRange,
        confidenceBase:   validator.confidenceBase,
      });
    }
  }, [validator?.id]);

  if (!validator) return null;
  const colors = PERSONA_COLORS[validator.color] ?? PERSONA_COLORS.indigo;

  function handleChange(key: string, value: number) {
    setLocal((prev) => ({ ...prev, [key]: value }));
    updateValidator(validator!.id, { [key]: value } as Partial<CustomValidator>);
  }

  return (
    <AnimatePresence>
      {validator && (
        <motion.div
          initial={{ x: 40, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: 40, opacity: 0 }}
          transition={{ type: "spring", stiffness: 280, damping: 28 }}
          className="fixed right-0 top-0 h-full w-[340px] bg-white border-l border-[#d8d4c8] shadow-xl z-50 overflow-y-auto"
        >
          <TooltipProvider>
            <div className="p-6">
              {/* Header */}
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div className={`h-9 w-9 rounded-lg flex items-center justify-center text-xs font-bold ${colors.bg} ${colors.text}`}>
                    {validator.avatar}
                  </div>
                  <div>
                    <h2 className="text-sm font-bold text-[#1a1a1a]">{validator.name}</h2>
                    <p className="text-xs text-[#6b6560]">Bias Editor</p>
                  </div>
                </div>
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0" onClick={onClose}>
                  <X className="h-4 w-4" />
                </Button>
              </div>

              <p className="text-xs text-[#6b6560] leading-relaxed mb-6">
                Adjust how this validator evaluates claims. Changes take effect immediately in the next simulation.
                Use the reset button on the card to restore defaults.
              </p>

              <Separator className="mb-6" />

              {/* Sliders */}
              <div className="space-y-7">
                {FIELDS.map((field) => (
                  <div key={field.key}>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-1.5">
                        <label className="text-sm font-medium text-[#1a1a1a]">{field.label}</label>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Info className="h-3.5 w-3.5 text-[#6b6560] cursor-help" />
                          </TooltipTrigger>
                          <TooltipContent className="max-w-[220px]">
                            {field.description}
                          </TooltipContent>
                        </Tooltip>
                      </div>
                      <span className="text-sm font-semibold text-[#2d2a26] tabular-nums">
                        {field.format(local[field.key] ?? validator[field.key])}
                      </span>
                    </div>
                    <Slider
                      min={field.min}
                      max={field.max}
                      step={field.step}
                      value={[local[field.key] ?? validator[field.key]]}
                      onValueChange={([v]) => handleChange(field.key, v)}
                    />
                    <div className="flex justify-between text-[10px] text-[#6b6560] mt-1.5">
                      <span>{field.format(field.min)}</span>
                      <span>{field.format(field.max)}</span>
                    </div>
                  </div>
                ))}
              </div>

              <Separator className="my-6" />

              {/* Persona preview */}
              <div className="rounded-lg bg-[#f5f2ec] p-4">
                <p className="text-xs font-semibold text-[#1a1a1a] mb-2">Behaviour Preview</p>
                <p className="text-xs text-[#6b6560] leading-relaxed">
                  With the current settings, <strong>{validator.name}</strong> will accept roughly{" "}
                  <strong>{Math.round((local.acceptThreshold ?? validator.acceptThreshold) * 100)}%</strong> of
                  neutral claims, show uncertainty within a{" "}
                  <strong>{Math.round((local.uncertaintyRange ?? validator.uncertaintyRange) * 100)}%</strong> band,
                  and report votes at an average confidence of{" "}
                  <strong>{Math.round((local.confidenceBase ?? validator.confidenceBase) * 100)}%</strong>.
                </p>
              </div>
            </div>
          </TooltipProvider>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
''')

# ─────────────────────────────────────────────────────────────────────────────
# 8. Vote History Table
# ─────────────────────────────────────────────────────────────────────────────
w("components/validators/VoteHistory.tsx", '''\
"use client";

import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, XCircle, HelpCircle, Trash2, Clock } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import type { CustomValidator, VoteRecord } from "@/store/validatorStore";

interface VoteHistoryProps {
  validator: CustomValidator;
  onClear: () => void;
}

const VOTE_ICONS = {
  ACCEPT:    { icon: CheckCircle2, variant: "accept"    as const, color: "text-green-600" },
  REJECT:    { icon: XCircle,      variant: "reject"    as const, color: "text-red-600" },
  UNCERTAIN: { icon: HelpCircle,   variant: "uncertain" as const, color: "text-amber-600" },
};

function timeAgo(ts: number): string {
  const s = Math.floor((Date.now() - ts) / 1000);
  if (s < 60) return `${s}s ago`;
  if (s < 3600) return `${Math.floor(s / 60)}m ago`;
  return `${Math.floor(s / 3600)}h ago`;
}

export function VoteHistory({ validator, onClear }: VoteHistoryProps) {
  const { voteHistory } = validator;

  if (voteHistory.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-[#d8d4c8] py-12 text-center">
        <p className="text-sm text-[#6b6560]">No vote history yet.</p>
        <p className="text-xs text-[#6b6560] mt-1">Run simulations in the Playground to see {validator.name}&apos;s votes here.</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-xs font-semibold text-[#6b6560] uppercase tracking-wider">
          Vote History · {voteHistory.length} records
        </p>
        <Button variant="ghost" size="sm" className="h-7 text-xs text-[#6b6560] hover:text-red-500" onClick={onClear}>
          <Trash2 className="h-3 w-3 mr-1" /> Clear
        </Button>
      </div>

      <AnimatePresence>
        {voteHistory.map((record, i) => (
          <VoteRow key={record.id} record={record} index={i} />
        ))}
      </AnimatePresence>
    </div>
  );
}

function VoteRow({ record, index }: { record: VoteRecord; index: number }) {
  const cfg = VOTE_ICONS[record.vote];
  const Icon = cfg.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: -6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.04 }}
      className="rounded-lg border border-[#e8e4da] bg-white/60 p-3.5"
    >
      <div className="flex items-start justify-between gap-3 mb-2">
        <p className="text-xs text-[#1a1a1a] leading-relaxed line-clamp-2 flex-1">
          {record.claim}
        </p>
        <div className="flex items-center gap-2 shrink-0">
          <Badge variant={cfg.variant} className="text-[10px] px-1.5 py-0">
            <Icon className="h-2.5 w-2.5 mr-0.5" /> {record.vote}
          </Badge>
        </div>
      </div>
      <div className="flex items-center gap-3">
        <div className="flex-1">
          <div className="flex justify-between text-[10px] text-[#6b6560] mb-1">
            <span>Confidence</span>
            <span className="font-medium">{Math.round(record.confidence * 100)}%</span>
          </div>
          <Progress value={Math.round(record.confidence * 100)} className="h-1" />
        </div>
        <div className="flex items-center gap-1 text-[10px] text-[#6b6560] shrink-0">
          <Clock className="h-2.5 w-2.5" /> {timeAgo(record.timestamp)}
        </div>
      </div>
      {record.reasoning && (
        <p className="text-[10px] text-[#6b6560] leading-relaxed mt-2 line-clamp-2 italic">
          &ldquo;{record.reasoning}&rdquo;
        </p>
      )}
    </motion.div>
  );
}
''')

# ─────────────────────────────────────────────────────────────────────────────
# 9. Comparison Panel
# ─────────────────────────────────────────────────────────────────────────────
w("components/validators/ComparisonPanel.tsx", '''\
"use client";

import { motion } from "framer-motion";
import { X, CheckCircle2, XCircle, HelpCircle, BarChart2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { PERSONA_COLORS } from "@/lib/validators/personas";
import type { CustomValidator } from "@/store/validatorStore";

interface ComparisonPanelProps {
  validators: CustomValidator[];
  onRemove: (id: string) => void;
  onClear: () => void;
}

const METRIC_ROWS = [
  { key: "acceptThreshold",  label: "Accept Threshold",  format: (v: number) => `${Math.round(v * 100)}%`, higher: "lenient" },
  { key: "confidenceBase",   label: "Base Confidence",   format: (v: number) => `${Math.round(v * 100)}%`, higher: "confident" },
  { key: "uncertaintyRange", label: "Uncertainty Range", format: (v: number) => `${Math.round(v * 100)}%`, higher: "more uncertain" },
] as const;

export function ComparisonPanel({ validators, onRemove, onClear }: ComparisonPanelProps) {
  if (validators.length === 0) {
    return (
      <div className="rounded-xl border-2 border-dashed border-[#d8d4c8] py-16 text-center">
        <BarChart2 className="h-8 w-8 text-[#d8d4c8] mx-auto mb-3" />
        <p className="text-sm font-medium text-[#1a1a1a]">No validators selected</p>
        <p className="text-xs text-[#6b6560] mt-1 max-w-xs mx-auto">
          Click &ldquo;Add to Comparison&rdquo; on up to 3 validator cards to compare their bias profiles side by side.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-[#d8d4c8] bg-white/60 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-3 border-b border-[#e8e4da]">
        <p className="text-sm font-semibold text-[#1a1a1a]">Validator Comparison</p>
        <Button variant="ghost" size="sm" className="text-xs h-7 text-[#6b6560]" onClick={onClear}>
          Clear all
        </Button>
      </div>

      {/* Validator columns */}
      <div className="grid gap-0" style={{ gridTemplateColumns: `140px repeat(${validators.length}, 1fr)` }}>
        {/* Column headers */}
        <div className="bg-[#f5f2ec] px-4 py-3 border-r border-[#e8e4da]" />
        {validators.map((v) => {
          const colors = PERSONA_COLORS[v.color] ?? PERSONA_COLORS.indigo;
          return (
            <div key={v.id} className="bg-[#f5f2ec] px-4 py-3 border-r border-[#e8e4da] last:border-r-0">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className={cn("h-7 w-7 rounded-lg flex items-center justify-center text-xs font-bold shrink-0", colors.bg, colors.text)}>
                    {v.avatar}
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-[#1a1a1a]">{v.name}</p>
                    <p className="text-[10px] text-[#6b6560] capitalize">{v.persona}</p>
                  </div>
                </div>
                <Button variant="ghost" size="sm" className="h-6 w-6 p-0 text-[#6b6560]" onClick={() => onRemove(v.id)}>
                  <X className="h-3 w-3" />
                </Button>
              </div>
            </div>
          );
        })}

        {/* Metric rows */}
        {METRIC_ROWS.map((row, ri) => (
          <>
            <div key={`label-${ri}`} className={cn("px-4 py-3 text-xs font-medium text-[#6b6560] border-r border-[#e8e4da]", ri % 2 === 0 ? "bg-white/40" : "bg-[#f5f2ec]/40")}>
              {row.label}
            </div>
            {validators.map((v) => {
              const val = v[row.key] as number;
              const maxVal = Math.max(...validators.map((x) => x[row.key] as number));
              const isMax = val === maxVal && validators.length > 1;
              return (
                <div key={`${v.id}-${row.key}`} className={cn("px-4 py-3 border-r border-[#e8e4da] last:border-r-0", ri % 2 === 0 ? "bg-white/40" : "bg-[#f5f2ec]/40")}>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className={cn("text-xs font-semibold", isMax ? "text-[#2d2a26]" : "text-[#6b6560]")}>
                      {row.format(val)}
                    </span>
                    {isMax && <span className="text-[9px] text-indigo-600 font-medium">highest</span>}
                  </div>
                  <Progress value={Math.round(val * 100)} className="h-1.5" />
                </div>
              );
            })}
          </>
        ))}

        {/* Vote stats rows (if any history) */}
        {validators.some((v) => v.totalVotes > 0) && (
          <>
            <div className="col-span-full px-5 py-2 bg-[#e8e4da]/50 border-t border-[#e8e4da]">
              <p className="text-[10px] font-semibold text-[#6b6560] uppercase tracking-wider">Historical Votes</p>
            </div>

            {/* Accept rate */}
            <div className="px-4 py-3 text-xs font-medium text-[#6b6560] border-r border-[#e8e4da] bg-white/40">
              Accept Rate
            </div>
            {validators.map((v) => (
              <div key={`${v.id}-accept`} className="px-4 py-3 border-r border-[#e8e4da] last:border-r-0 bg-white/40">
                {v.totalVotes > 0 ? (
                  <div className="flex items-center gap-1.5">
                    <CheckCircle2 className="h-3 w-3 text-green-500 shrink-0" />
                    <span className="text-xs font-semibold text-green-700">{Math.round(v.acceptRate * 100)}%</span>
                  </div>
                ) : (
                  <span className="text-[10px] text-[#d8d4c8]">—</span>
                )}
              </div>
            ))}

            {/* Reject rate */}
            <div className="px-4 py-3 text-xs font-medium text-[#6b6560] border-r border-[#e8e4da] bg-[#f5f2ec]/40">
              Reject Rate
            </div>
            {validators.map((v) => (
              <div key={`${v.id}-reject`} className="px-4 py-3 border-r border-[#e8e4da] last:border-r-0 bg-[#f5f2ec]/40">
                {v.totalVotes > 0 ? (
                  <div className="flex items-center gap-1.5">
                    <XCircle className="h-3 w-3 text-red-500 shrink-0" />
                    <span className="text-xs font-semibold text-red-700">{Math.round(v.rejectRate * 100)}%</span>
                  </div>
                ) : (
                  <span className="text-[10px] text-[#d8d4c8]">—</span>
                )}
              </div>
            ))}

            {/* Uncertain rate */}
            <div className="px-4 py-3 text-xs font-medium text-[#6b6560] border-r border-[#e8e4da] bg-white/40">
              Uncertain Rate
            </div>
            {validators.map((v) => (
              <div key={`${v.id}-uncertain`} className="px-4 py-3 border-r border-[#e8e4da] last:border-r-0 bg-white/40">
                {v.totalVotes > 0 ? (
                  <div className="flex items-center gap-1.5">
                    <HelpCircle className="h-3 w-3 text-amber-500 shrink-0" />
                    <span className="text-xs font-semibold text-amber-700">{Math.round(v.uncertainRate * 100)}%</span>
                  </div>
                ) : (
                  <span className="text-[10px] text-[#d8d4c8]">—</span>
                )}
              </div>
            ))}
          </>
        )}
      </div>
    </div>
  );
}
''')

# ─────────────────────────────────────────────────────────────────────────────
# 10. Network Stats Bar
# ─────────────────────────────────────────────────────────────────────────────
w("components/validators/NetworkStats.tsx", '''\
"use client";

import { Users, TrendingUp, Zap, Activity } from "lucide-react";
import type { CustomValidator } from "@/store/validatorStore";

interface NetworkStatsProps {
  validators: CustomValidator[];
}

export function NetworkStats({ validators: vv }: NetworkStatsProps) {
  const withHistory = vv.filter((v) => v.totalVotes > 0);
  const totalVotes  = vv.reduce((s, v) => s + v.totalVotes, 0);
  const avgAccept   = withHistory.length > 0
    ? withHistory.reduce((s, v) => s + v.acceptRate, 0) / withHistory.length
    : null;
  const avgConf     = withHistory.length > 0
    ? withHistory.reduce((s, v) => s + v.avgConfidence, 0) / withHistory.length
    : null;
  const modified    = vv.filter((v) => v.isCustom).length;

  const stats = [
    { icon: Users,     label: "Active Validators", value: `${vv.length}`, sub: `${modified} modified` },
    { icon: Activity,  label: "Total Votes Cast",  value: totalVotes > 0 ? `${totalVotes}` : "—", sub: "across all validators" },
    { icon: TrendingUp,label: "Avg Accept Rate",   value: avgAccept != null ? `${Math.round(avgAccept * 100)}%` : "—", sub: "network-wide" },
    { icon: Zap,       label: "Avg Confidence",    value: avgConf != null ? `${Math.round(avgConf * 100)}%` : "—", sub: "base level" },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
      {stats.map((s) => (
        <div key={s.label} className="rounded-xl border border-[#d8d4c8] bg-white/60 p-4">
          <div className="flex items-center gap-2 mb-2">
            <s.icon className="h-4 w-4 text-[#6b6560]" />
            <span className="text-xs text-[#6b6560]">{s.label}</span>
          </div>
          <p className="text-xl font-bold text-[#1a1a1a] leading-tight">{s.value}</p>
          <p className="text-[10px] text-[#6b6560] mt-0.5">{s.sub}</p>
        </div>
      ))}
    </div>
  );
}
''')

# ─────────────────────────────────────────────────────────────────────────────
# 11. Validator Lab Page
# ─────────────────────────────────────────────────────────────────────────────
w("app/(dashboard)/validator-lab/page.tsx", '''\
"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { useValidatorStore, type CustomValidator } from "@/store/validatorStore";
import { ValidatorProfile } from "@/components/validators/ValidatorProfile";
import { BiasEditor } from "@/components/validators/BiasEditor";
import { VoteHistory } from "@/components/validators/VoteHistory";
import { ComparisonPanel } from "@/components/validators/ComparisonPanel";
import { NetworkStats } from "@/components/validators/NetworkStats";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";

export default function ValidatorLabPage() {
  const {
    validators,
    selectedValidatorId,
    comparisonIds,
    selectValidator,
    toggleComparison,
    clearComparison,
    updateValidator,
    resetValidator,
    clearHistory,
  } = useValidatorStore();

  const [editingId, setEditingId] = useState<string | null>(null);

  const selectedValidator = validators.find((v) => v.id === selectedValidatorId) ?? null;
  const editingValidator  = validators.find((v) => v.id === editingId) ?? null;
  const comparedValidators = validators.filter((v) => comparisonIds.includes(v.id));

  return (
    <div className="min-h-screen bg-[#efece4]">
      {/* Bias Editor slide-out */}
      <BiasEditor
        validator={editingValidator}
        onClose={() => setEditingId(null)}
      />

      <div className="mx-auto max-w-7xl px-6 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-[#1a1a1a] tracking-tight mb-2">Validator Lab</h1>
          <p className="text-[#6b6560] text-sm max-w-2xl leading-relaxed">
            Explore the five GenLayer validator nodes. Adjust their bias profiles, review their vote
            histories, and compare them side-by-side to understand how different LLM personas
            influence consensus outcomes.
          </p>
        </div>

        {/* Network-wide stats */}
        <NetworkStats validators={validators} />

        <Tabs defaultValue="validators">
          <TabsList className="mb-6">
            <TabsTrigger value="validators">Validator Roster</TabsTrigger>
            <TabsTrigger value="compare">
              Comparison
              {comparisonIds.length > 0 && (
                <span className="ml-1.5 h-4 w-4 rounded-full bg-[#2d2a26] text-[#efece4] text-[9px] flex items-center justify-center">
                  {comparisonIds.length}
                </span>
              )}
            </TabsTrigger>
            {selectedValidator && (
              <TabsTrigger value="history">
                {selectedValidator.name}&apos;s History
              </TabsTrigger>
            )}
          </TabsList>

          {/* ── Roster tab ── */}
          <TabsContent value="validators">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
              {validators.map((v) => (
                <ValidatorProfile
                  key={v.id}
                  validator={v}
                  isSelected={selectedValidatorId === v.id}
                  isInComparison={comparisonIds.includes(v.id)}
                  onSelect={() => selectValidator(v.id)}
                  onToggleComparison={() => toggleComparison(v.id)}
                  onEdit={() => setEditingId(v.id)}
                  onReset={() => resetValidator(v.id)}
                />
              ))}
            </div>

            {/* Selected validator detail */}
            {selectedValidator && (
              <motion.div
                key={selectedValidator.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-6 rounded-xl border border-[#d8d4c8] bg-white/60 p-6"
              >
                <h3 className="text-sm font-semibold text-[#1a1a1a] mb-1">
                  About {selectedValidator.name}
                </h3>
                <p className="text-sm text-[#6b6560] leading-relaxed mb-4">
                  {selectedValidator.description}
                </p>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
                  {[
                    { label: "Model", value: selectedValidator.model },
                    { label: "Persona", value: selectedValidator.persona },
                    { label: "Accept Bias", value: `${Math.round(selectedValidator.acceptThreshold * 100)}%` },
                    { label: "Confidence", value: `${Math.round(selectedValidator.confidenceBase * 100)}%` },
                  ].map((item) => (
                    <div key={item.label} className="rounded-lg bg-[#f5f2ec] p-3">
                      <p className="text-xs text-[#6b6560] mb-0.5">{item.label}</p>
                      <p className="text-sm font-semibold text-[#1a1a1a]">{item.value}</p>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </TabsContent>

          {/* ── Comparison tab ── */}
          <TabsContent value="compare">
            <ComparisonPanel
              validators={comparedValidators}
              onRemove={(id) => toggleComparison(id)}
              onClear={clearComparison}
            />
          </TabsContent>

          {/* ── History tab ── */}
          {selectedValidator && (
            <TabsContent value="history">
              <VoteHistory
                validator={selectedValidator}
                onClear={() => clearHistory(selectedValidator.id)}
              />
            </TabsContent>
          )}
        </Tabs>
      </div>
    </div>
  );
}
''')

# ─────────────────────────────────────────────────────────────────────────────
# 12. Wire vote history: update simulationService to record votes in store
#     (adds a thin bridge — the service calls the store after each vote)
# ─────────────────────────────────────────────────────────────────────────────
w("lib/validators/recordVotes.ts", '''\
/**
 * Bridge: after a simulation finishes, persist each validator\'s vote
 * into the ValidatorStore so the Validator Lab history tab stays current.
 *
 * Called from the playground page after runSimulation() resolves.
 */
import type { SimulationRun } from "@/services/simulationService";
import { useValidatorStore } from "@/store/validatorStore";

export function recordSimulationVotes(run: SimulationRun): void {
  const { addVoteRecord, validators } = useValidatorStore.getState();

  for (const lv of run.validators) {
    if (lv.status !== "voted" || !lv.vote) continue;

    // Match by name (personas are seeded as default_0..4)
    const storeValidator = validators.find((sv) => sv.name === lv.name);
    if (!storeValidator) continue;

    addVoteRecord(storeValidator.id, {
      claim:        run.claim,
      category:     run.category,
      vote:         lv.vote,
      confidence:   lv.confidence ?? 0,
      reasoning:    lv.reasoning ?? "",
      simulationId: run.id,
    });
  }
}
''')

# ─────────────────────────────────────────────────────────────────────────────
# 13. Update playground page to call recordSimulationVotes after completion
# ─────────────────────────────────────────────────────────────────────────────
w("app/(dashboard)/playground/page.tsx", '''\
"use client";

import { useCallback, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { runSimulation, runAppeal, type SimulationRun } from "@/services/simulationService";
import { useSimulationStore } from "@/store/simulationStore";
import { recordSimulationVotes } from "@/lib/validators/recordVotes";
import { ClaimForm } from "@/components/consensus/ClaimForm";
import { ValidatorCard } from "@/components/validators/ValidatorCard";
import { ConsensusStatus } from "@/components/consensus/ConsensusStatus";
import { ConsensusTimeline } from "@/components/consensus/ConsensusTimeline";
import { SimulationResult } from "@/components/consensus/SimulationResult";
import { AppealTrigger } from "@/components/appeals/AppealTrigger";

export default function PlaygroundPage() {
  const { currentRun, isRunning, setCurrentRun, clearCurrentRun, addToHistory } = useSimulationStore();
  const [localRun, setLocalRun] = useState<SimulationRun | null>(null);

  const activeRun = localRun ?? currentRun;

  const handleSimulate = useCallback(async (claim: string, category: string) => {
    setLocalRun(null);
    const finalRun = await runSimulation(claim, category, (update) => {
      setLocalRun({ ...update });
      setCurrentRun({ ...update });
    });
    recordSimulationVotes(finalRun);
    addToHistory(finalRun);
  }, [setCurrentRun, addToHistory]);

  const handleAppeal = useCallback(async (reason: string) => {
    if (!activeRun) return;
    const finalRun = await runAppeal(activeRun, reason, (update) => {
      setLocalRun({ ...update });
      setCurrentRun({ ...update });
    });
    recordSimulationVotes(finalRun);
    addToHistory(finalRun);
  }, [activeRun, setCurrentRun, addToHistory]);

  const handleReset = useCallback(() => {
    setLocalRun(null);
    clearCurrentRun();
  }, [clearCurrentRun]);

  const status = activeRun?.status ?? "idle";
  const showAppeal = status === "appeal_triggered" && !isRunning;
  const showResult = ["accepted", "rejected", "appeal_triggered", "finalized"].includes(status) && !isRunning;
  const showValidators = activeRun && activeRun.validators.length > 0;

  return (
    <div className="min-h-screen bg-[#efece4]">
      <div className="mx-auto max-w-7xl px-6 py-8">

        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-[#1a1a1a] tracking-tight mb-2">
            Consensus Playground
          </h1>
          <p className="text-[#6b6560] text-sm max-w-2xl leading-relaxed">
            Submit a subjective claim and watch GenLayer&apos;s Optimistic Democracy in action.
            Five AI validators independently evaluate the claim and attempt to reach consensus
            through the Equivalence Principle.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

          {/* Left column — form + timeline + result */}
          <div className="lg:col-span-1 space-y-4">
            <AnimatePresence>
              {(!activeRun || showResult) && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                  <ClaimForm onSubmit={handleSimulate} disabled={isRunning} />
                </motion.div>
              )}
            </AnimatePresence>

            {activeRun && <ConsensusStatus status={status} round={activeRun.round} />}
            {activeRun && <ConsensusTimeline status={status} />}
            {showAppeal && <AppealTrigger onAppeal={handleAppeal} disabled={isRunning} />}

            {showResult && activeRun?.consensusResult && !showAppeal && (
              <SimulationResult run={activeRun} onReset={handleReset} onAppeal={handleAppeal} />
            )}
          </div>

          {/* Right column — validators */}
          <div className="lg:col-span-2">
            {!showValidators ? (
              <div className="h-full rounded-xl border-2 border-dashed border-[#d8d4c8] flex flex-col items-center justify-center py-20 text-center px-8">
                <div className="text-4xl mb-4">⚡</div>
                <h3 className="text-base font-semibold text-[#1a1a1a] mb-2">Waiting for a claim</h3>
                <p className="text-sm text-[#6b6560] max-w-xs leading-relaxed">
                  Submit a claim on the left to start the simulation. Watch 5 AI validators
                  independently reason about your claim in real time.
                </p>
                <div className="mt-6 flex flex-wrap gap-2 justify-center text-xs text-[#6b6560]">
                  {["Analytical", "Creative", "Strict", "Lenient", "Balanced"].map((p) => (
                    <span key={p} className="rounded-full border border-[#e8e4da] bg-white/50 px-3 py-1">{p}</span>
                  ))}
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-sm font-semibold text-[#1a1a1a]">
                    Validator Network
                    {activeRun.round > 1 && (
                      <span className="ml-2 text-xs text-purple-600 font-normal">Appeal Round {activeRun.round}</span>
                    )}
                  </h2>
                  <span className="text-xs text-[#6b6560]">
                    {activeRun.validators.filter((v) => v.status === "voted").length} / {activeRun.validators.length} voted
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3">
                  <AnimatePresence>
                    {activeRun.validators.map((validator, i) => (
                      <ValidatorCard key={validator.id} validator={validator} index={i} />
                    ))}
                  </AnimatePresence>
                </div>

                {isRunning && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="rounded-lg border border-[#d8d4c8] bg-white/40 p-3 text-xs text-[#6b6560] leading-relaxed"
                  >
                    <span className="font-medium text-[#1a1a1a]">Equivalence Principle: </span>
                    Each validator runs the claim through its assigned LLM independently.
                    Results are compared — if 60%+ agree, consensus is reached. Otherwise, an appeal is triggered.
                  </motion.div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
''')

# ─────────────────────────────────────────────────────────────────────────────
# 14. Check @radix-ui/react-slider, react-tabs, react-separator, react-tooltip
#     are in package.json — add them if missing
# ─────────────────────────────────────────────────────────────────────────────
import json

pkg_path = ROOT / "package.json"
pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
deps = pkg.get("dependencies", {})

needed = {
    "@radix-ui/react-slider":    "^1.2.3",
    "@radix-ui/react-tabs":      "^1.1.3",
    "@radix-ui/react-separator": "^1.1.2",
    "@radix-ui/react-tooltip":   "^1.2.7",
}

added = []
for pkg_name, ver in needed.items():
    if pkg_name not in deps:
        deps[pkg_name] = ver
        added.append(pkg_name)

if added:
    pkg["dependencies"] = deps
    pkg_path.write_text(json.dumps(pkg, indent=2), encoding="utf-8")
    print(f"\n  ADDED to package.json: {', '.join(added)}")
else:
    print("\n  package.json: all Radix deps already present")

print("\nPhase 5 setup complete. All files written.\n")
