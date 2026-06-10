"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Search, ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";
import { GLOSSARY_TERMS } from "@/lib/learn/content";

export function Glossary() {
  const [query,    setQuery]    = useState("");
  const [expanded, setExpanded] = useState<string | null>(null);

  const categories = [...new Set(GLOSSARY_TERMS.map((t) => t.category))].sort();
  const filtered   = GLOSSARY_TERMS.filter((t) =>
    !query || t.term.toLowerCase().includes(query.toLowerCase()) || t.definition.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="space-y-4">
      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[#6b6560]" />
        <input
          type="text"
          placeholder="Search terms…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-[#d8d4c8] bg-white/60 text-sm text-[#1a1a1a] placeholder:text-[#6b6560] focus:outline-none focus:ring-2 focus:ring-[#2d2a26]/20"
        />
      </div>

      {/* Terms by category */}
      {(query ? ["Search Results"] : categories).map((cat) => {
        const terms = query
          ? filtered
          : filtered.filter((t) => t.category === cat);
        if (terms.length === 0) return null;

        return (
          <div key={cat}>
            {!query && (
              <p className="text-[10px] font-semibold text-[#6b6560] uppercase tracking-wider mb-2">{cat}</p>
            )}
            <div className="space-y-1.5">
              {terms.map((term) => (
                <div key={term.term} className="rounded-xl border border-[#d8d4c8] bg-white/60 overflow-hidden">
                  <button
                    onClick={() => setExpanded(expanded === term.term ? null : term.term)}
                    className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-[#f5f2ec] transition-colors"
                  >
                    <span className="text-sm font-semibold text-[#1a1a1a]">{term.term}</span>
                    <ChevronDown className={cn("h-4 w-4 text-[#6b6560] transition-transform shrink-0", expanded === term.term && "rotate-180")} />
                  </button>
                  <AnimatePresence>
                    {expanded === term.term && (
                      <motion.div
                        initial={{ height: 0 }}
                        animate={{ height: "auto" }}
                        exit={{ height: 0 }}
                        className="overflow-hidden"
                      >
                        <div className="px-4 pb-4 border-t border-[#e8e4da] pt-3">
                          <p className="text-xs text-[#6b6560] leading-relaxed">{term.definition}</p>
                          {term.relatedTerms.length > 0 && (
                            <div className="mt-3 flex flex-wrap gap-1.5">
                              <span className="text-[10px] text-[#6b6560]">Related:</span>
                              {term.relatedTerms.map((r) => (
                                <button key={r} onClick={() => setExpanded(r)}
                                  className="text-[10px] text-indigo-600 hover:underline">{r}</button>
                              ))}
                            </div>
                          )}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
