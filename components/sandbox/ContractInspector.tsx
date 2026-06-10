"use client";

import { useMemo } from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { parseContract } from "@/lib/sandbox/parser";
import { AlertTriangle, Eye, Edit3, Cpu, Database } from "lucide-react";

interface ContractInspectorProps {
  code: string;
}

export function ContractInspector({ code }: ContractInspectorProps) {
  const parsed = useMemo(() => parseContract(code), [code]);

  if (!parsed.name) {
    return (
      <div className="text-center py-6 text-[#6b6560] text-xs">
        No valid GenLayer contract detected.<br />
        Class must inherit <code className="bg-[#e8e4da] px-1 rounded">gl.Contract</code>.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Contract name */}
      <div>
        <p className="text-[11px] font-semibold text-[#6b6560] uppercase tracking-wider mb-1.5">Contract</p>
        <div className="flex items-center gap-2 bg-[#2d2a26] rounded-lg px-3 py-2">
          <Cpu className="h-3.5 w-3.5 text-[#efece4]/60 shrink-0" />
          <span className="text-xs font-bold text-[#efece4] font-mono">{parsed.name}</span>
          {parsed.hasExecPrompt && (
            <span className="ml-auto text-[9px] bg-purple-500/30 text-purple-200 px-1.5 py-0.5 rounded-full font-semibold">
              AI-powered
            </span>
          )}
        </div>
      </div>

      {/* Errors */}
      {parsed.errors.length > 0 && (
        <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 space-y-1">
          {parsed.errors.map((e, i) => (
            <div key={i} className="flex items-start gap-1.5 text-xs text-amber-800">
              <AlertTriangle className="h-3 w-3 mt-0.5 shrink-0" />
              {e}
            </div>
          ))}
        </div>
      )}

      {/* State variables */}
      {parsed.stateVars.length > 0 && (
        <div>
          <p className="text-[11px] font-semibold text-[#6b6560] uppercase tracking-wider mb-1.5 flex items-center gap-1">
            <Database className="h-3 w-3" /> State ({parsed.stateVars.length})
          </p>
          <div className="space-y-1">
            {parsed.stateVars.map((sv) => (
              <div key={sv.name} className="flex items-center justify-between bg-[#f5f2ea] rounded px-2.5 py-1.5">
                <span className="text-xs font-mono text-[#1a1a1a] font-medium">{sv.name}</span>
                <span className="text-[10px] font-mono text-[#6b6560] bg-[#e8e4da] px-1.5 rounded">{sv.type}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Functions */}
      {parsed.functions.length > 0 && (
        <div>
          <p className="text-[11px] font-semibold text-[#6b6560] uppercase tracking-wider mb-1.5">
            Functions ({parsed.functions.length})
          </p>
          <div className="space-y-1.5">
            {parsed.functions.map((fn, i) => (
              <motion.div
                key={fn.name}
                initial={{ opacity: 0, y: 4 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.04 }}
                className={cn(
                  "rounded-lg border px-2.5 py-2",
                  fn.decorator === "@gl.public.write"
                    ? "border-purple-200 bg-purple-50"
                    : fn.decorator === "@gl.public.view"
                    ? "border-blue-200 bg-blue-50"
                    : "border-[#e8e4da] bg-[#f5f2ea]"
                )}
              >
                <div className="flex items-center gap-1.5 mb-0.5">
                  {fn.decorator === "@gl.public.write" ? (
                    <Edit3 className="h-3 w-3 text-purple-500 shrink-0" />
                  ) : fn.decorator === "@gl.public.view" ? (
                    <Eye className="h-3 w-3 text-blue-500 shrink-0" />
                  ) : null}
                  <span className="text-xs font-mono font-bold text-[#1a1a1a]">{fn.name}()</span>
                  <span className="ml-auto text-[9px] font-mono text-[#6b6560]">→ {fn.returnsType}</span>
                </div>
                {fn.decorator !== "constructor" && (
                  <div className={cn(
                    "text-[9px] font-semibold px-1.5 py-0.5 rounded-full w-fit",
                    fn.decorator === "@gl.public.write"
                      ? "bg-purple-100 text-purple-700"
                      : "bg-blue-100 text-blue-700"
                  )}>
                    {fn.decorator}
                  </div>
                )}
                {fn.params.length > 0 && (
                  <div className="mt-1 flex flex-wrap gap-1">
                    {fn.params.map((p) => (
                      <span key={p} className="text-[9px] font-mono bg-white/70 border border-[#d8d4c8] px-1.5 py-0.5 rounded text-[#6b6560]">
                        {p}
                      </span>
                    ))}
                  </div>
                )}
                {fn.docstring && (
                  <p className="text-[10px] text-[#6b6560] mt-1 leading-snug">{fn.docstring}</p>
                )}
              </motion.div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
