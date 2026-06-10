"use client";

import { useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface SandboxConsoleProps {
  lines: string[];
  isRunning: boolean;
}

function colorize(line: string): string {
  return line; // passed as text, color via className logic
}

function getLineStyle(line: string): string {
  if (line.includes("[consensus]"))   return "text-purple-400";
  if (line.includes("[equivalence]")) return "text-blue-400";
  if (line.includes("[validator:"))   return "text-green-400";
  if (line.includes("[sandbox]"))     return "text-[#efece4]/80";
  if (line.includes("ERROR"))         return "text-red-400";
  return "text-[#8a8680]";
}

export function SandboxConsole({ lines, isRunning }: SandboxConsoleProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [lines]);

  return (
    <div className="h-full bg-[#141414] rounded-xl border border-[#2d2a26] overflow-hidden flex flex-col">
      <div className="flex items-center gap-2 px-4 py-2 border-b border-[#2d2a26] bg-[#1a1a1a]">
        <div className="flex gap-1.5">
          <div className="h-3 w-3 rounded-full bg-[#ff5f57]" />
          <div className="h-3 w-3 rounded-full bg-[#febc2e]" />
          <div className="h-3 w-3 rounded-full bg-[#28c840]" />
        </div>
        <span className="text-[11px] text-[#5a5550] font-mono ml-2">GenLayer Sandbox Console</span>
        {isRunning && (
          <span className="ml-auto flex items-center gap-1.5 text-[10px] text-green-400 font-mono">
            <span className="h-1.5 w-1.5 rounded-full bg-green-400 animate-pulse" />
            executing...
          </span>
        )}
      </div>
      <div className="flex-1 overflow-y-auto px-4 py-3 font-mono text-[11px] leading-5 space-y-0.5">
        {lines.length === 0 ? (
          <p className="text-[#3a3530]">$ waiting for execution...</p>
        ) : (
          lines.map((line, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: i * 0.03 }}
              className={cn("whitespace-pre-wrap break-all", getLineStyle(line))}
            >
              {line}
            </motion.div>
          ))
        )}
        {isRunning && (
          <div className="text-green-400 animate-pulse">▋</div>
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
