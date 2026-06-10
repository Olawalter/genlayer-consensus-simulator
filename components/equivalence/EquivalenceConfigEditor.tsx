"use client";

import { cn } from "@/lib/utils";
import { Slider } from "@/components/ui/slider";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import type { EquivalenceConfig } from "@/lib/equivalence/scorer";

interface EquivalenceConfigEditorProps {
  config: EquivalenceConfig;
  onChange: (cfg: EquivalenceConfig) => void;
}

export function EquivalenceConfigEditor({ config, onChange }: EquivalenceConfigEditorProps) {
  return (
    <div className="rounded-xl border border-[#d8d4c8] bg-white/60 p-5 space-y-5">
      <div>
        <p className="text-sm font-semibold text-[#1a1a1a] mb-1">Equivalence Mode</p>
        <p className="text-xs text-[#6b6560] leading-relaxed mb-3">
          GenLayer contracts declare which mode applies. Comparative checks if outputs are
          numerically close. Non-comparative checks if each output independently meets criteria.
        </p>
        <div className="flex gap-2">
          {(["comparative", "non_comparative"] as const).map((m) => (
            <button
              key={m}
              onClick={() => {
                if (m === "comparative") {
                  onChange({ mode: "comparative", marginPercent: 20, threshold: 0.6 });
                } else {
                  onChange({ mode: "non_comparative", criteria: "meets quality standard", threshold: 0.6 });
                }
              }}
              className={cn(
                "flex-1 text-xs rounded-lg border-2 px-3 py-2 font-medium transition-all",
                config.mode === m
                  ? "border-[#2d2a26] bg-[#2d2a26] text-[#efece4]"
                  : "border-[#d8d4c8] text-[#6b6560] hover:border-[#b8b4a8]"
              )}
            >
              {m === "comparative" ? "Comparative" : "Non-Comparative"}
            </button>
          ))}
        </div>
      </div>

      <Separator />

      {/* Agreement threshold (shared) */}
      <div>
        <div className="flex justify-between mb-2">
          <Label className="text-xs font-medium">Agreement Threshold</Label>
          <span className="text-xs font-semibold text-[#2d2a26]">{Math.round(config.threshold * 100)}%</span>
        </div>
        <Slider
          min={0.5} max={1} step={0.05}
          value={[config.threshold]}
          onValueChange={([v]) => onChange({ ...config, threshold: v })}
        />
        <p className="text-[10px] text-[#6b6560] mt-1.5">
          Minimum fraction of validators that must agree for equivalence to pass.
          GenLayer default is 60%.
        </p>
      </div>

      {/* Mode-specific controls */}
      {config.mode === "comparative" && (
        <div>
          <div className="flex justify-between mb-2">
            <Label className="text-xs font-medium">Equivalence Margin</Label>
            <span className="text-xs font-semibold text-[#2d2a26]">±{config.marginPercent / 2}%</span>
          </div>
          <Slider
            min={4} max={50} step={2}
            value={[config.marginPercent]}
            onValueChange={([v]) => onChange({ ...config, marginPercent: v })}
          />
          <p className="text-[10px] text-[#6b6560] mt-1.5">
            How wide the equivalence band is around the mean output. Wider = more lenient.
          </p>
        </div>
      )}

      {config.mode === "non_comparative" && (
        <div className="rounded-lg bg-[#f5f2ec] p-3 text-xs text-[#6b6560] leading-relaxed">
          <strong className="text-[#1a1a1a]">Non-Comparative mode:</strong> Each validator independently
          evaluates whether the output meets the contract-defined criteria. Outputs scoring ≥ 50% are
          considered as &ldquo;meets criteria&rdquo;. No margin is needed — votes are binary.
        </div>
      )}
    </div>
  );
}
