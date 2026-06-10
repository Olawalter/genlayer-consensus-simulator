"use client";

import { useState } from "react";
import { Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

const EXAMPLE_CLAIMS = [
  {
    category: "freelance",
    text: "The freelancer delivered a fully functional e-commerce website with all agreed-upon features, including payment integration and mobile responsiveness, by the deadline.",
  },
  {
    category: "review",
    text: "This product review is genuine — the reviewer purchased the item, used it for 30 days, and their feedback accurately reflects a real user experience.",
  },
  {
    category: "event",
    text: "The charity fundraiser event raised over $50,000 for the designated cause, and all proceeds were transferred to the charity within 7 days of the event.",
  },
  {
    category: "custom",
    text: "The software audit was completed in accordance with the agreed security standards and all critical vulnerabilities identified were properly disclosed to the client.",
  },
];

interface ClaimFormProps {
  onSubmit: (claim: string, category: string) => void;
  disabled?: boolean;
}

export function ClaimForm({ onSubmit, disabled }: ClaimFormProps) {
  const [claim, setClaim] = useState("");
  const [category, setCategory] = useState("freelance");

  function handleExampleClick(example: typeof EXAMPLE_CLAIMS[0]) {
    setClaim(example.text);
    setCategory(example.category);
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!claim.trim()) return;
    onSubmit(claim.trim(), category);
  }

  return (
    <div className="rounded-xl border border-[#d8d4c8] bg-white/60 backdrop-blur-sm p-6">
      <h2 className="text-base font-semibold text-[#1a1a1a] mb-1">Submit a Claim</h2>
      <p className="text-xs text-[#6b6560] mb-5 leading-relaxed">
        Enter any subjective claim. The GenLayer validator network will independently evaluate it
        and attempt to reach consensus using the Equivalence Principle.
      </p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-1.5">
          <Label htmlFor="category" className="text-xs">Category</Label>
          <Select value={category} onValueChange={setCategory} disabled={disabled}>
            <SelectTrigger className="h-9 text-sm">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="freelance">Freelance Work</SelectItem>
              <SelectItem value="review">Product Review</SelectItem>
              <SelectItem value="event">Event / Real-World Claim</SelectItem>
              <SelectItem value="custom">Custom</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="claim" className="text-xs">Claim</Label>
          <Textarea
            id="claim"
            placeholder="Describe the subjective claim you want validators to evaluate..."
            value={claim}
            onChange={(e) => setClaim(e.target.value)}
            className="min-h-[100px] text-sm"
            disabled={disabled}
          />
          <p className="text-[11px] text-[#6b6560]">{claim.length} characters</p>
        </div>

        <Button
          type="submit"
          className="w-full"
          disabled={disabled || !claim.trim()}
        >
          <Send className="h-4 w-4 mr-2" />
          Submit to Validator Network
        </Button>
      </form>

      {/* Examples */}
      <div className="mt-5 pt-4 border-t border-[#e8e4da]">
        <p className="text-[11px] font-medium text-[#6b6560] uppercase tracking-wider mb-3">
          Example Claims
        </p>
        <div className="space-y-2">
          {EXAMPLE_CLAIMS.map((ex, i) => (
            <button
              key={i}
              onClick={() => handleExampleClick(ex)}
              disabled={disabled}
              className="w-full text-left text-xs text-[#6b6560] hover:text-[#1a1a1a] rounded-lg border border-[#e8e4da] hover:border-[#d8d4c8] bg-white/40 hover:bg-white/70 px-3 py-2.5 transition-all leading-relaxed"
            >
              <span className="font-medium text-[#2d2a26]">[{ex.category}]</span>{" "}
              {ex.text.slice(0, 90)}...
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
