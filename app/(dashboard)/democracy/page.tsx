"use client";

import { useDemocracyStore } from "@/store/democracyStore";
import { DemocracyStats } from "@/components/democracy/DemocracyStats";
import { LiveTxRunner } from "@/components/democracy/LiveTxRunner";
import { TxFeedCard } from "@/components/democracy/TxFeedCard";
import { TxLifecycleStep } from "@/components/democracy/TxLifecycleStep";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Trash2 } from "lucide-react";

export default function DemocracyPage() {
  const { transactions, activeId, setActiveId, clearTransactions, networkStats } = useDemocracyStore();
  const activeTx = transactions.find((t) => t.id === activeId) ?? null;

  return (
    <div className="min-h-screen bg-[#efece4]">
      <div className="mx-auto max-w-7xl px-6 py-8">

        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-[#1a1a1a] tracking-tight mb-2">
            Optimistic Democracy Dashboard
          </h1>
          <p className="text-[#6b6560] text-sm max-w-2xl leading-relaxed">
            GenLayer&apos;s Optimistic Democracy is the governance mechanism that turns individual
            validator votes into on-chain outcomes. Submit a claim and trace every step of its
            lifecycle — from proposal through validator review, equivalence check, finality
            window, and final commitment.
          </p>
        </div>

        {/* Stats */}
        <DemocracyStats stats={networkStats} />

        <Tabs defaultValue="submit">
          <TabsList className="mb-6">
            <TabsTrigger value="submit">Submit Transaction</TabsTrigger>
            <TabsTrigger value="feed">
              Transaction Feed
              {transactions.length > 0 && (
                <span className="ml-1.5 h-4 min-w-4 rounded-full bg-[#2d2a26] text-[#efece4] text-[9px] flex items-center justify-center px-1">
                  {transactions.length}
                </span>
              )}
            </TabsTrigger>
          </TabsList>

          {/* ── Submit ── */}
          <TabsContent value="submit">
            <div className="max-w-2xl">
              <LiveTxRunner />
            </div>
          </TabsContent>

          {/* ── Feed ── */}
          <TabsContent value="feed">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Left: transaction list */}
              <div>
                <div className="flex items-center justify-between mb-3">
                  <p className="text-xs font-semibold text-[#6b6560] uppercase tracking-wider">
                    {transactions.length} transactions
                  </p>
                  {transactions.length > 0 && (
                    <Button variant="ghost" size="sm" className="h-7 text-xs text-[#6b6560] hover:text-red-500"
                      onClick={clearTransactions}>
                      <Trash2 className="h-3 w-3 mr-1" /> Clear
                    </Button>
                  )}
                </div>

                {transactions.length === 0 ? (
                  <div className="rounded-xl border border-dashed border-[#d8d4c8] py-12 text-center">
                    <p className="text-sm text-[#6b6560]">No transactions yet.</p>
                    <p className="text-xs text-[#6b6560] mt-1">Submit a claim to see it here.</p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {transactions.map((tx, i) => (
                      <TxFeedCard key={tx.id} tx={tx} isActive={activeId === tx.id}
                        onClick={() => setActiveId(tx.id)} index={i} />
                    ))}
                  </div>
                )}
              </div>

              {/* Right: detail */}
              {activeTx && (
                <div className="space-y-4">
                  <TxLifecycleStep stage={activeTx.stage} />

                  <div className="rounded-xl border border-[#d8d4c8] bg-white/60 p-5 space-y-3">
                    <p className="text-xs font-semibold text-[#6b6560] uppercase tracking-wider">Claim</p>
                    <p className="text-sm text-[#1a1a1a] leading-relaxed">&ldquo;{activeTx.claim}&rdquo;</p>

                    <div className="grid grid-cols-2 gap-3 pt-2 border-t border-[#e8e4da]">
                      {[
                        { label: "Outcome",          value: activeTx.outcome },
                        { label: "Equivalence Score",value: `${Math.round(activeTx.equivalenceScore * 100)}%` },
                        { label: "Round",             value: `${activeTx.round}` },
                        { label: "Block",             value: `#${activeTx.blockHeight}` },
                      ].map((item) => (
                        <div key={item.label} className="rounded-lg bg-[#f5f2ec] p-2.5">
                          <p className="text-[10px] text-[#6b6560] mb-0.5">{item.label}</p>
                          <p className="text-xs font-semibold text-[#1a1a1a]">{item.value}</p>
                        </div>
                      ))}
                    </div>

                    <div className="pt-2 border-t border-[#e8e4da]">
                      <p className="text-[10px] font-semibold text-[#6b6560] mb-2">Validator Votes</p>
                      <div className="flex flex-wrap gap-1.5">
                        {activeTx.validatorVotes.map((v) => (
                          <span key={v.name} className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${
                            v.vote === "ACCEPT" ? "bg-green-100 text-green-700" :
                            v.vote === "REJECT" ? "bg-red-100 text-red-700" : "bg-amber-100 text-amber-700"
                          }`}>
                            {v.name} · {v.vote} ({Math.round(v.confidence * 100)}%)
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </TabsContent>
        </Tabs>

        {/* Educational cards */}
        <div className="mt-10 grid grid-cols-1 sm:grid-cols-3 gap-4">
          {[
            {
              title: "Optimistic Execution",
              body: "Like Optimistic Rollups, GenLayer assumes transactions are valid and processes them immediately. The challenge period allows anyone to dispute outcomes before they are finalised.",
            },
            {
              title: "The Finality Window",
              body: "After validators reach consensus, a finality window opens (typically 5–10 blocks). Any stakeholder can challenge the outcome. If no valid challenge arrives, the result is committed to the state tree.",
            },
            {
              title: "On-Chain Settlement",
              body: "Once finality is reached, the contract state is updated. For Intelligent Contracts, this means the `@gl.public.write` function's side-effects are persisted — permanently and immutably.",
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
