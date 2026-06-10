"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Scale, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";

interface AppealTriggerProps {
  onAppeal: (reason: string) => void;
  disabled?: boolean;
}

export function AppealTrigger({ onAppeal, disabled }: AppealTriggerProps) {
  const [reason, setReason] = useState("");
  const [open, setOpen] = useState(false);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!reason.trim()) return;
    onAppeal(reason.trim());
    setOpen(false);
    setReason("");
  }

  return (
    <div className="rounded-xl border-2 border-purple-200 bg-purple-50 p-5">
      <div className="flex items-start gap-3 mb-4">
        <AlertTriangle className="h-5 w-5 text-purple-600 shrink-0 mt-0.5" />
        <div>
          <p className="text-sm font-semibold text-purple-800">Appeal Available</p>
          <p className="text-xs text-purple-600 mt-0.5 leading-relaxed">
            The validator network is split. Under Optimistic Democracy, you can trigger an appeal
            which adds 3 more validators to re-evaluate this claim.
          </p>
        </div>
      </div>

      {!open ? (
        <Button
          onClick={() => setOpen(true)}
          disabled={disabled}
          className="w-full bg-purple-700 hover:bg-purple-800 text-white"
          size="sm"
        >
          <Scale className="h-4 w-4 mr-2" />
          Trigger Appeal Round
        </Button>
      ) : (
        <motion.form
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          onSubmit={handleSubmit}
          className="space-y-3"
        >
          <div className="space-y-1.5">
            <Label className="text-xs text-purple-800">Appeal Reason</Label>
            <Textarea
              placeholder="Explain why you believe the initial consensus was incorrect..."
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              className="text-sm min-h-[80px] border-purple-200 focus-visible:ring-purple-400 bg-white/80"
            />
          </div>
          <div className="flex gap-2">
            <Button type="submit" size="sm" disabled={!reason.trim() || disabled}
              className="flex-1 bg-purple-700 hover:bg-purple-800 text-white">
              Submit Appeal
            </Button>
            <Button type="button" variant="ghost" size="sm" onClick={() => setOpen(false)}>
              Cancel
            </Button>
          </div>
        </motion.form>
      )}
    </div>
  );
}
