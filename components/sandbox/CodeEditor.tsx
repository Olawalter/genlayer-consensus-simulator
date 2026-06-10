"use client";

import { useRef, useEffect, useCallback } from "react";
import { cn } from "@/lib/utils";

interface CodeEditorProps {
  value: string;
  onChange: (v: string) => void;
  disabled?: boolean;
}

export function CodeEditor({ value, onChange, disabled }: CodeEditorProps) {
  const taRef = useRef<HTMLTextAreaElement>(null);
  const linesRef = useRef<HTMLDivElement>(null);

  const lines = value.split("\n");

  // Sync scroll between textarea and line numbers
  const syncScroll = useCallback(() => {
    if (taRef.current && linesRef.current) {
      linesRef.current.scrollTop = taRef.current.scrollTop;
    }
  }, []);

  useEffect(() => {
    const ta = taRef.current;
    if (!ta) return;
    ta.addEventListener("scroll", syncScroll);
    return () => ta.removeEventListener("scroll", syncScroll);
  }, [syncScroll]);

  // Tab key support
  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Tab") {
      e.preventDefault();
      const ta = taRef.current!;
      const start = ta.selectionStart;
      const end = ta.selectionEnd;
      const newVal = value.slice(0, start) + "    " + value.slice(end);
      onChange(newVal);
      requestAnimationFrame(() => {
        ta.selectionStart = ta.selectionEnd = start + 4;
      });
    }
  }

  return (
    <div className="relative flex rounded-xl border border-[#2d2a26] overflow-hidden bg-[#1a1a1a] font-mono text-xs leading-6 h-full">
      {/* Line numbers */}
      <div
        ref={linesRef}
        className="select-none overflow-hidden bg-[#141414] text-[#5a5550] text-right pr-3 pl-3 pt-4 pb-4 min-w-[3rem] border-r border-[#2d2a26]"
        style={{ overflowY: "hidden" }}
        aria-hidden
      >
        {lines.map((_, i) => (
          <div key={i} className="leading-6">{i + 1}</div>
        ))}
      </div>

      {/* Editable area */}
      <textarea
        ref={taRef}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        onScroll={syncScroll}
        disabled={disabled}
        spellCheck={false}
        autoCapitalize="off"
        autoCorrect="off"
        className={cn(
          "flex-1 resize-none outline-none bg-transparent text-[#e8e4da] caret-[#efece4]",
          "px-4 py-4 leading-6 whitespace-pre overflow-auto",
          disabled && "opacity-50 cursor-not-allowed"
        )}
        style={{ fontFamily: "ui-monospace, 'Cascadia Code', 'Fira Code', Consolas, monospace" }}
      />
    </div>
  );
}
