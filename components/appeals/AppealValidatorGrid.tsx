"use client";

import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, XCircle, HelpCircle, Crown, Cpu, Shield } from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { PERSONA_COLORS } from "@/lib/validators/personas";
import type { AppealValidatorUpdate } from "@/services/appealService";

interface AppealValidatorGridProps {
  validators: AppealValidatorUpdate[];
}

const VOTE_CFG = {
  ACCEPT:    { icon: CheckCircle2, variant: "accept"    as const },
  REJECT:    { icon: XCircle,      variant: "reject"    as const },
  UNCERTAIN: { icon: HelpCircle,   variant: "uncertain" as const },
};

export function AppealValidatorGrid({ validators }: AppealValidatorGridProps) {
  const original = validators.filter((v) => v.isOriginal);
  const appeal   = validators.filter((v) => !v.isOriginal);

  return (
    <div className="space-y-5">
      {/* Original validators */}
      {original.length > 0 && (
        <div>
          <p className="text-[11px] font-semibold text-[#6b6560] uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
            <Crown className="h-3 w-3" /> Original Validators (Round 1)
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2">
            {original.map((v, i) => (
              <ValidatorMiniCard key={v.id} validator={v} index={i} dimmed />
            ))}
          </div>
        </div>
      )}

      {/* Appeal validators */}
      {appeal.length > 0 && (
        <div>
          <p className="text-[11px] font-semibold text-purple-700 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
            <Shield className="h-3 w-3" /> Appeal Validators (Round {appeal[0]?.round})
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2">
            {appeal.map((v, i) => (
              <ValidatorMiniCard key={v.id} validator={v} index={i} highlight />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function ValidatorMiniCard({
  validator: v,
  index,
  dimmed,
  highlight,
}: {
  validator: AppealValidatorUpdate;
  index: number;
  dimmed?: boolean;
  highlight?: boolean;
}) {
  const colors = PERSONA_COLORS[v.color] ?? PERSONA_COLORS.indigo;
  const voteCfg = v.vote ? VOTE_CFG[v.vote] : null;
  const Icon = voteCfg?.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: dimmed ? 0.7 : 1, y: 0 }}
      transition={{ delay: index * 0.07 }}
      className={cn(
        "rounded-lg border p-3 text-center",
        highlight && v.status === "thinking" && "border-purple-300 bg-purple-50",
        highlight && v.status === "voted"   && "border-purple-200 bg-purple-50/50",
        highlight && v.status === "waiting" && "border-[#d8d4c8] bg-white/40",
        dimmed && "border-[#e8e4da] bg-white/30",
      )}
    >
      <div className={cn("h-8 w-8 rounded-lg flex items-center justify-center text-xs font-bold mx-auto mb-2", colors.bg, colors.text)}>
        {v.avatar}
      </div>
      <p className="text-[10px] font-semibold text-[#1a1a1a] leading-tight truncate">{v.name.split(" ")[0]}</p>
      <p className="text-[9px] text-[#6b6560] flex items-center justify-center gap-0.5 mt-0.5">
        <Cpu className="h-2 w-2" /> {v.model.split("-")[0]}
      </p>

      <div className="mt-2">
        {v.status === "waiting" && <span className="h-1.5 w-1.5 rounded-full bg-[#d8d4c8] inline-block" />}
        {v.status === "thinking" && (
          <span className="flex justify-center gap-0.5">
            {[0, 1, 2].map((i) => (
              <motion.span
                key={i}
                className="h-1 w-1 rounded-full bg-purple-500 inline-block"
                animate={{ opacity: [0.3, 1, 0.3] }}
                transition={{ duration: 1, repeat: Infinity, delay: i * 0.2 }}
              />
            ))}
          </span>
        )}
        {v.status === "voted" && voteCfg && Icon && (
          <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: "spring", stiffness: 300 }}>
            <Badge variant={voteCfg.variant} className="text-[9px] px-1.5 py-0">
              <Icon className="h-2.5 w-2.5 mr-0.5" /> {v.vote}
            </Badge>
            <div className="mt-1">
              <Progress value={Math.round((v.confidence ?? 0) * 100)} className="h-0.5" />
              <p className="text-[9px] text-[#6b6560] mt-0.5">{Math.round((v.confidence ?? 0) * 100)}%</p>
            </div>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
}
