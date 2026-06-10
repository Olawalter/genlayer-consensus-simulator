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
