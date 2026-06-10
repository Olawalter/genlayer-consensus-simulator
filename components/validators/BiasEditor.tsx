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
