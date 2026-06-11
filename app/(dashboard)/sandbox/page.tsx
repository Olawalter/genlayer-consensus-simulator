"use client";

import { useState, useCallback, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Play, RotateCcw, Wifi, WifiOff } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { CONTRACT_TEMPLATES } from "@/lib/sandbox/templates";
import { executeSandboxContract } from "@/lib/sandbox/executor";
import { parseContract } from "@/lib/sandbox/parser";
import { useSandboxStore } from "@/store/sandboxStore";
import { CodeEditor } from "@/components/sandbox/CodeEditor";
import { TemplateSelector } from "@/components/sandbox/TemplateSelector";
import { ContractInspector } from "@/components/sandbox/ContractInspector";
import { ExecutionPanel } from "@/components/sandbox/ExecutionPanel";
import { SandboxConsole } from "@/components/sandbox/SandboxConsole";

const DEFAULT_CODE  = CONTRACT_TEMPLATES[0].code;
const DEFAULT_INPUT = CONTRACT_TEMPLATES[0].defaultInput;

export default function SandboxPage() {
  const {
    code, activeTemplateId, functionInput, isRunning, currentResult,
    setCode, setActiveTemplate, setFunctionInput, setIsRunning, setCurrentResult,
  } = useSandboxStore();

  const [consoleLines, setConsoleLines] = useState<string[]>([]);
  const [chainStatus, setChainStatus]   = useState<string>("");

  const effectiveCode  = code  || DEFAULT_CODE;
  const effectiveInput = functionInput || DEFAULT_INPUT;
  const parsed  = useMemo(() => parseContract(effectiveCode), [effectiveCode]);
  const writeFn = parsed.functions.find((f) => f.decorator === "@gl.public.write");

  const isRealChain = !!(process.env.NEXT_PUBLIC_GENLAYER_PRIVATE_KEY);

  async function handleRun() {
    if (!writeFn) return;
    setIsRunning(true);
    setConsoleLines([]);
    setChainStatus("");

    try {
      const result = await executeSandboxContract(
        effectiveCode,
        writeFn.name,
        effectiveInput,
        (status, detail) => {
          setChainStatus(detail ?? status);
          setConsoleLines((prev) => [...prev, `[${status}] ${detail ?? ""}`]);
        }
      );
      setCurrentResult(result);
      setConsoleLines(result.consoleLog);
    } catch (err) {
      setConsoleLines([`[ERROR] ${String(err)}`]);
    } finally {
      setIsRunning(false);
      setChainStatus("");
    }
  }

  function handleSelectTemplate(t: typeof CONTRACT_TEMPLATES[0]) {
    setCode(t.code);
    setFunctionInput(t.defaultInput);
    setActiveTemplate(t.id);
    setCurrentResult(null);
    setConsoleLines([]);
  }

  function handleReset() {
    setCode("");
    setFunctionInput("");
    setActiveTemplate(null);
    setCurrentResult(null);
    setConsoleLines([]);
    setIsRunning(false);
  }

  return (
    <div className="min-h-screen bg-[#efece4]">
      <div className="mx-auto max-w-7xl px-6 py-8 space-y-6">

        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-[#1a1a1a]">Contract Sandbox</h1>
            <p className="text-sm text-[#6b6560] mt-1">
              Write and execute Intelligent Contracts on GenLayer
            </p>
          </div>
          <div className="flex items-center gap-2">
            {/* Chain mode indicator */}
            <div className={cn(
              "flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium",
              isRealChain
                ? "border-green-300 bg-green-50 text-green-700"
                : "border-amber-300 bg-amber-50 text-amber-700"
            )}>
              {isRealChain
                ? <><Wifi className="h-3 w-3" /> Studio Net</>
                : <><WifiOff className="h-3 w-3" /> Simulated</>
              }
            </div>
            <Button variant="ghost" size="sm" onClick={handleReset} className="gap-1.5 text-xs h-8">
              <RotateCcw className="h-3.5 w-3.5" /> Reset
            </Button>
          </div>
        </div>

        {/* Template selector */}
        <TemplateSelector
          activeId={activeTemplateId}
          onSelect={handleSelectTemplate}
        />

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left: editor + inspector */}
          <div className="space-y-4">
            <CodeEditor
              value={effectiveCode}
              onChange={setCode}
            />
            <ContractInspector code={effectiveCode} />
          </div>

          {/* Right: run panel + console */}
          <div className="space-y-4">
            <div className="rounded-xl border border-[#d8d4c8] bg-white p-4 space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <p className="text-xs font-medium text-[#1a1a1a]">
                    Function: <code className="text-[#6b6560]">{writeFn?.name ?? "—"}</code>
                  </p>
                  <p className="text-xs text-[#6b6560]">Input argument</p>
                </div>
                <Button
                  onClick={handleRun}
                  disabled={isRunning || !writeFn}
                  size="sm"
                  className="gap-1.5 text-xs h-8 bg-[#2d2a26] text-[#efece4] hover:bg-[#1a1a1a]"
                >
                  <Play className="h-3.5 w-3.5" />
                  {isRunning ? (isRealChain ? "On-chain..." : "Simulating...") : "Run"}
                </Button>
              </div>

              <input
                type="text"
                value={effectiveInput}
                onChange={(e) => setFunctionInput(e.target.value)}
                placeholder="Enter input for the write function..."
                className="w-full rounded-lg border border-[#d8d4c8] bg-[#f8f6f0] px-3 py-2 text-sm text-[#1a1a1a] placeholder:text-[#9e9891] focus:outline-none focus:ring-2 focus:ring-[#2d2a26]/20"
              />

              {/* Chain status during execution */}
              <AnimatePresence>
                {isRunning && chainStatus && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="rounded-lg bg-blue-50 border border-blue-200 px-3 py-2 text-xs text-blue-700"
                  >
                    <span className="font-medium">
                      {isRealChain ? "⛓ On-chain: " : "⚙ "}
                    </span>
                    {chainStatus}
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Real chain tx link */}
              {currentResult?.realChain && (
                <div className="rounded-lg bg-green-50 border border-green-200 px-3 py-2 text-xs text-green-800 space-y-1">
                  <p className="font-medium">On-chain result</p>
                  <p>Status: <span className="font-mono">{currentResult.realChain.status}</span></p>
                  <p className="font-mono truncate">Tx: {currentResult.realChain.txHash}</p>
                  {currentResult.realChain.contractAddress && (
                    <p className="font-mono truncate">Contract: {currentResult.realChain.contractAddress}</p>
                  )}
                </div>
              )}
            </div>

            <AnimatePresence mode="wait">
              {currentResult && (
                <motion.div
                  key="result"
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                >
                  <ExecutionPanel result={currentResult} />
                </motion.div>
              )}
            </AnimatePresence>

            <SandboxConsole lines={consoleLines} isRunning={isRunning} />
          </div>
        </div>
      </div>
    </div>
  );
}
