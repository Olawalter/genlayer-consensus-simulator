"use client";

import { useState, useCallback, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Play, RotateCcw, ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { CONTRACT_TEMPLATES } from "@/lib/sandbox/templates";
import { executeSandboxContract } from "@/lib/sandbox/executor";
import { parseContract } from "@/lib/sandbox/parser";
import { useSandboxStore } from "@/store/sandboxStore";
import { CodeEditor } from "@/components/sandbox/CodeEditor";
import { TemplateSelector } from "@/components/sandbox/TemplateSelector";
import { ContractInspector } from "@/components/sandbox/ContractInspector";
import { ExecutionPanel } from "@/components/sandbox/ExecutionPanel";
import { SandboxConsole } from "@/components/sandbox/SandboxConsole";

const DEFAULT_CODE = CONTRACT_TEMPLATES[0].code;
const DEFAULT_INPUT = CONTRACT_TEMPLATES[0].defaultInput;

export default function SandboxPage() {
  const {
    code, activeTemplateId, functionInput, isRunning, currentResult, selectedValidatorIndex,
    setCode, setActiveTemplate, setFunctionInput, setIsRunning, setCurrentResult,
  } = useSandboxStore();

  const [consoleLines, setConsoleLines] = useState<string[]>([]);

  const effectiveCode = code || DEFAULT_CODE;
  const effectiveInput = functionInput || DEFAULT_INPUT;

  const parsed = useMemo(() => parseContract(effectiveCode), [effectiveCode]);

  // First write function (the one we execute)
  const writeFn = parsed.functions.find((f) => f.decorator === "@gl.public.write");

  async function handleRun() {
    if (!writeFn) return;
    setIsRunning(true);
    setConsoleLines([]);

    try {
      const result = await executeSandboxContract(
        effectiveCode,
        writeFn.name,
        effectiveInput
      );
      setCurrentResult(result);
      setConsoleLines(result.consoleLog);
    } catch (err) {
      setConsoleLines([`[ERROR] ${String(err)}`]);
    } finally {
      setIsRunning(false);
    }
  }

  function handleSelectTemplate(t: typeof CONTRACT_TEMPLATES[0]) {
    setCode(t.code);
    setFunctionInput(t.defaultInput);
    setActiveTemplate(t.id);
  }

  function handleReset() {
    setCode("");
    setFunctionInput("");
    setActiveTemplate(null);
    setConsoleLines([]);
  }

  return (
    <div className="min-h-screen bg-[#efece4]">
      <div className="mx-auto max-w-[1600px] px-4 py-6">

        {/* Header */}
        <div className="flex items-start justify-between mb-5">
          <div>
            <h1 className="text-2xl font-bold text-[#1a1a1a] tracking-tight mb-1">Developer Sandbox</h1>
            <p className="text-sm text-[#6b6560] max-w-xl leading-relaxed">
              Write Intelligent Contracts in Python, execute them through a simulated 5-validator
              GenLayer consensus, and watch the Equivalence Principle resolve non-deterministic LLM outputs in real time.
            </p>
          </div>
          <div className="flex items-center gap-2 shrink-0 ml-4">
            <Button variant="outline" size="sm" onClick={handleReset} className="gap-1.5">
              <RotateCcw className="h-3.5 w-3.5" /> Reset
            </Button>
            <Button
              size="sm"
              onClick={handleRun}
              disabled={isRunning || !writeFn}
              className="gap-1.5 bg-[#2d2a26] hover:bg-[#1a1a1a] text-[#efece4] min-w-[120px]"
            >
              {isRunning ? (
                <><span className="h-3.5 w-3.5 border-2 border-[#efece4]/40 border-t-[#efece4] rounded-full animate-spin" /> Running...</>
              ) : (
                <><Play className="h-3.5 w-3.5" /> Run Contract</>
              )}
            </Button>
          </div>
        </div>

        {/* Main layout: sidebar | editor | results */}
        <div className="grid grid-cols-[220px_1fr_380px] gap-4 h-[calc(100vh-160px)] min-h-[600px]">

          {/* LEFT — Template selector + Inspector */}
          <div className="flex flex-col gap-4 overflow-y-auto pr-1">
            <TemplateSelector
              activeId={activeTemplateId}
              onSelect={handleSelectTemplate}
            />
            <div className="border-t border-[#d8d4c8] pt-4">
              <p className="text-[11px] font-semibold text-[#6b6560] uppercase tracking-wider mb-2">Inspector</p>
              <ContractInspector code={effectiveCode} />
            </div>
          </div>

          {/* CENTER — Code editor + input bar */}
          <div className="flex flex-col gap-3 min-h-0">
            {/* Input bar */}
            <div className="flex items-center gap-2 bg-white/60 border border-[#d8d4c8] rounded-xl px-3 py-2">
              <div className="flex items-center gap-1.5 shrink-0">
                <span className="text-[10px] font-mono text-[#6b6560] bg-[#e8e4da] px-2 py-0.5 rounded">
                  {writeFn ? `${writeFn.name}(` : "no @write fn"}
                </span>
              </div>
              <input
                type="text"
                value={effectiveInput}
                onChange={(e) => setFunctionInput(e.target.value)}
                placeholder="Function input string..."
                disabled={isRunning}
                className="flex-1 text-xs bg-transparent outline-none text-[#1a1a1a] placeholder:text-[#b8b4a8] font-mono"
              />
              {writeFn && (
                <span className="text-[10px] font-mono text-[#6b6560] shrink-0">)</span>
              )}
              {!writeFn && (
                <span className="text-[10px] text-amber-600 shrink-0">
                  Add a @gl.public.write function to enable execution
                </span>
              )}
            </div>

            {/* Editor */}
            <div className="flex-1 min-h-0">
              <CodeEditor
                value={effectiveCode}
                onChange={setCode}
                disabled={isRunning}
              />
            </div>
          </div>

          {/* RIGHT — Results + Console */}
          <div className="flex flex-col min-h-0">
            <Tabs defaultValue="results" className="flex flex-col h-full">
              <TabsList className="mb-3 shrink-0">
                <TabsTrigger value="results">Results</TabsTrigger>
                <TabsTrigger value="console">Console</TabsTrigger>
              </TabsList>

              <TabsContent value="results" className="flex-1 overflow-hidden">
                {currentResult ? (
                  <ExecutionPanel result={currentResult} />
                ) : (
                  <div className="h-full rounded-xl border-2 border-dashed border-[#d8d4c8] flex flex-col items-center justify-center text-center px-6 py-12">
                    <div className="text-4xl mb-4">⚡</div>
                    <h3 className="text-sm font-bold text-[#1a1a1a] mb-2">No execution yet</h3>
                    <p className="text-xs text-[#6b6560] max-w-xs leading-relaxed">
                      Select a template or write your own contract, then click
                      <strong> Run Contract</strong> to see all 5 validators
                      execute and reach consensus.
                    </p>
                    <div className="mt-5 flex flex-col gap-1.5 text-left w-full max-w-[220px]">
                      {["5 validators execute in parallel", "Each calls its assigned LLM", "Equivalence Principle resolves votes", "Final outcome written on-chain"].map((step, i) => (
                        <div key={i} className="flex items-center gap-2 text-xs text-[#6b6560]">
                          <span className="h-5 w-5 rounded-full bg-[#e8e4da] text-[10px] flex items-center justify-center font-bold shrink-0">{i + 1}</span>
                          {step}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </TabsContent>

              <TabsContent value="console" className="flex-1 overflow-hidden">
                <SandboxConsole lines={consoleLines} isRunning={isRunning} />
              </TabsContent>
            </Tabs>
          </div>
        </div>

        {/* Educational callout */}
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-5 grid grid-cols-1 sm:grid-cols-3 gap-4"
        >
          {[
            {
              icon: "🐍",
              title: "Python-native",
              body: "Write contracts in standard Python. The GenVM executes them with full access to the gl module — no Solidity or new languages to learn.",
            },
            {
              icon: "🤖",
              title: "gl.exec_prompt()",
              body: "Every call to gl.exec_prompt() reaches the validator's assigned LLM. Five validators = five independent AI calls, each potentially returning a different answer.",
            },
            {
              icon: "⚖️",
              title: "Equivalence resolves disagreements",
              body: "When validators disagree, the Equivalence Principle determines whether the spread of votes is acceptable. If not, an appeal is triggered automatically.",
            },
          ].map((card) => (
            <div key={card.title} className="rounded-xl border border-[#d8d4c8] bg-white/60 p-4">
              <div className="text-2xl mb-2">{card.icon}</div>
              <h3 className="text-sm font-bold text-[#1a1a1a] mb-1">{card.title}</h3>
              <p className="text-xs text-[#6b6560] leading-relaxed">{card.body}</p>
            </div>
          ))}
        </motion.div>
      </div>
    </div>
  );
}
