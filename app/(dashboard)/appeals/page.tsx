"use client";

import { useAppealStore } from "@/store/appealStore";
import { AppealStats } from "@/components/appeals/AppealStats";
import { AppealHistory } from "@/components/appeals/AppealHistory";
import { AppealDetail } from "@/components/appeals/AppealDetail";
import { LiveAppealRunner } from "@/components/appeals/LiveAppealRunner";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";

export default function AppealsPage() {
  const { appeals, activeAppealId, setActiveAppeal, clearAppeals } = useAppealStore();
  const activeAppeal = appeals.find((a) => a.id === activeAppealId) ?? null;

  return (
    <div className="min-h-screen bg-[#efece4]">
      <div className="mx-auto max-w-7xl px-6 py-8">

        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-[#1a1a1a] tracking-tight mb-2">Appeals Arena</h1>
          <p className="text-[#6b6560] text-sm max-w-2xl leading-relaxed">
            When GenLayer validators can&apos;t reach consensus, an appeal is triggered. The validator
            set expands, new evaluators weigh in, and the Equivalence Principle is re-applied across
            the full pool. Explore past appeals or run a live appeal simulation.
          </p>
        </div>

        <AppealStats appeals={appeals} />

        <Tabs defaultValue="simulate">
          <TabsList className="mb-6">
            <TabsTrigger value="simulate">Live Simulation</TabsTrigger>
            <TabsTrigger value="history">
              Appeal History
              {appeals.length > 0 && (
                <span className="ml-1.5 h-4 min-w-4 rounded-full bg-[#2d2a26] text-[#efece4] text-[9px] flex items-center justify-center px-1">
                  {appeals.length}
                </span>
              )}
            </TabsTrigger>
            {activeAppeal && (
              <TabsTrigger value="detail">Case Detail</TabsTrigger>
            )}
          </TabsList>

          {/* ── Live simulation ── */}
          <TabsContent value="simulate">
            <div className="max-w-2xl">
              <LiveAppealRunner />
            </div>
          </TabsContent>

          {/* ── History ── */}
          <TabsContent value="history">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <AppealHistory
                appeals={appeals}
                activeId={activeAppealId}
                onSelect={setActiveAppeal}
                onClear={clearAppeals}
              />
              {activeAppeal && (
                <AppealDetail appeal={activeAppeal} />
              )}
            </div>
          </TabsContent>

          {/* ── Case detail ── */}
          {activeAppeal && (
            <TabsContent value="detail">
              <div className="max-w-2xl">
                <AppealDetail appeal={activeAppeal} />
              </div>
            </TabsContent>
          )}
        </Tabs>

        {/* Educational callout */}
        <div className="mt-10 grid grid-cols-1 sm:grid-cols-3 gap-4">
          {[
            {
              title: "Why Appeals Exist",
              body: "Subjective claims don't always have a clear right answer. When validators genuinely disagree, an appeal adds more perspectives rather than forcing a premature consensus.",
            },
            {
              title: "Validator Expansion",
              body: "Each appeal round adds 3 more validators. Their votes are pooled with all previous rounds. The Equivalence Principle is applied across the full pool each time.",
            },
            {
              title: "Finality Window",
              body: "Once consensus is reached — even after multiple rounds — a finality window opens. The outcome is committed to the GenLayer state tree after this window expires.",
            },
          ].map((card) => (
            <div key={card.title} className="rounded-xl border border-[#d8d4c8] bg-white/40 p-5">
              <h3 className="text-sm font-semibold text-[#1a1a1a] mb-2">{card.title}</h3>
              <p className="text-xs text-[#6b6560] leading-relaxed">{card.body}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
