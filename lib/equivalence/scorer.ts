/**
 * Extended equivalence scoring utilities for the Equivalence Explorer.
 * Supports both Comparative and Non-Comparative modes as defined in GenLayer.
 */

export type EquivalenceMode = "comparative" | "non_comparative";

export interface ComparativeConfig {
  mode: "comparative";
  marginPercent: number;   // 0–50: how wide the equivalence band is
  threshold: number;       // 0–1: minimum agreement ratio
}

export interface NonComparativeConfig {
  mode: "non_comparative";
  criteria: string;        // human-readable criteria description
  threshold: number;       // 0–1: minimum agreement ratio
}

export type EquivalenceConfig = ComparativeConfig | NonComparativeConfig;

export interface VoteInput {
  label: string;
  value: number;   // 0–1 normalised score (1 = accept)
}

export interface EquivalenceScoreResult {
  mode: EquivalenceMode;
  votes: VoteInput[];
  agreement: number;         // 0–1 how much votes cluster
  withinMargin: number;      // count of votes within margin of the mean
  outsideMargin: number;
  mean: number;
  spread: number;            // standard deviation
  passes: boolean;
  bandLow: number;
  bandHigh: number;
  explanation: string;
}

export function scoreComparative(
  votes: VoteInput[],
  cfg: ComparativeConfig
): EquivalenceScoreResult {
  const values = votes.map((v) => v.value);
  const mean   = values.reduce((s, v) => s + v, 0) / values.length;
  const spread = Math.sqrt(values.reduce((s, v) => s + (v - mean) ** 2, 0) / values.length);

  const halfBand  = cfg.marginPercent / 100 / 2;
  const bandLow   = Math.max(0, mean - halfBand);
  const bandHigh  = Math.min(1, mean + halfBand);

  const withinMargin  = values.filter((v) => v >= bandLow && v <= bandHigh).length;
  const outsideMargin = values.length - withinMargin;
  const agreement     = withinMargin / values.length;
  const passes        = agreement >= cfg.threshold;

  const explanation = passes
    ? `${withinMargin}/${votes.length} validator outputs fall within the ±${cfg.marginPercent / 2}% equivalence band around the mean (${Math.round(mean * 100)}%). Comparative equivalence is satisfied.`
    : `Only ${withinMargin}/${votes.length} outputs are within the equivalence band. The spread of ${Math.round(spread * 100)}% exceeds what comparative equivalence allows. An appeal would be triggered.`;

  return { mode: "comparative", votes, agreement, withinMargin, outsideMargin, mean, spread, passes, bandLow, bandHigh, explanation };
}

export function scoreNonComparative(
  votes: VoteInput[],
  cfg: NonComparativeConfig
): EquivalenceScoreResult {
  // Non-comparative: each output is independently judged against criteria.
  // value >= 0.5 → meets criteria; value < 0.5 → does not meet criteria.
  const meetsCriteria = votes.filter((v) => v.value >= 0.5).length;
  const agreement     = meetsCriteria / votes.length;
  const passes        = agreement >= cfg.threshold;
  const mean          = votes.reduce((s, v) => s + v.value, 0) / votes.length;
  const spread        = Math.sqrt(votes.reduce((s, v) => s + (v.value - mean) ** 2, 0) / votes.length);

  const explanation = passes
    ? `${meetsCriteria}/${votes.length} validators judged the output as meeting the criteria "${cfg.criteria}". Non-comparative equivalence is satisfied.`
    : `Only ${meetsCriteria}/${votes.length} validators found the output meets "${cfg.criteria}". Non-comparative equivalence fails — the claim does not consistently satisfy the defined criteria.`;

  return { mode: "non_comparative", votes, agreement, withinMargin: meetsCriteria, outsideMargin: votes.length - meetsCriteria, mean, spread, passes, bandLow: 0.5, bandHigh: 1, explanation };
}

export function computeEquivalenceDetailed(
  votes: VoteInput[],
  cfg: EquivalenceConfig
): EquivalenceScoreResult {
  return cfg.mode === "comparative"
    ? scoreComparative(votes, cfg)
    : scoreNonComparative(votes, cfg);
}

// ── Pre-built scenarios for the explorer ─────────────────────────────────────

export interface ExplorerScenario {
  id: string;
  title: string;
  description: string;
  mode: EquivalenceMode;
  claim: string;
  votes: VoteInput[];
  config: EquivalenceConfig;
  category: string;
}

export const EXPLORER_SCENARIOS: ExplorerScenario[] = [
  {
    id: "s1",
    title: "Unanimous Accept",
    description: "All five validators strongly agree the claim meets the criteria.",
    mode: "comparative",
    category: "unanimous",
    claim: "The freelancer delivered the website on time with all agreed features.",
    votes: [
      { label: "Atlas",  value: 0.92 },
      { label: "Nova",   value: 0.89 },
      { label: "Orion",  value: 0.88 },
      { label: "Lyra",   value: 0.94 },
      { label: "Zephyr", value: 0.91 },
    ],
    config: { mode: "comparative", marginPercent: 20, threshold: 0.6 },
  },
  {
    id: "s2",
    title: "Majority Accept",
    description: "Four validators accept, one strict validator rejects. Equivalence still passes.",
    mode: "comparative",
    category: "majority",
    claim: "The product review reflects a genuine user experience with fair criticism.",
    votes: [
      { label: "Atlas",  value: 0.75 },
      { label: "Nova",   value: 0.82 },
      { label: "Orion",  value: 0.28 },
      { label: "Lyra",   value: 0.80 },
      { label: "Zephyr", value: 0.71 },
    ],
    config: { mode: "comparative", marginPercent: 30, threshold: 0.6 },
  },
  {
    id: "s3",
    title: "Split — Appeal Triggered",
    description: "Validators are evenly split. Agreement falls below 60% threshold.",
    mode: "comparative",
    category: "split",
    claim: "The consultant substantially completed the project to industry standard.",
    votes: [
      { label: "Atlas",  value: 0.62 },
      { label: "Nova",   value: 0.58 },
      { label: "Orion",  value: 0.31 },
      { label: "Lyra",   value: 0.74 },
      { label: "Zephyr", value: 0.40 },
    ],
    config: { mode: "comparative", marginPercent: 20, threshold: 0.6 },
  },
  {
    id: "s4",
    title: "Non-Comparative: Criteria Met",
    description: "Each validator independently checks whether the output meets the defined criteria.",
    mode: "non_comparative",
    category: "non_comparative",
    claim: "This AI-generated summary is factually accurate and unbiased.",
    votes: [
      { label: "Atlas",  value: 0.80 },
      { label: "Nova",   value: 0.71 },
      { label: "Orion",  value: 0.55 },
      { label: "Lyra",   value: 0.88 },
      { label: "Zephyr", value: 0.62 },
    ],
    config: { mode: "non_comparative", criteria: "factually accurate and unbiased", threshold: 0.6 },
  },
  {
    id: "s5",
    title: "Narrow Margin",
    description: "Votes cluster tightly — barely within the equivalence band. Tests the boundary.",
    mode: "comparative",
    category: "edge",
    claim: "The event raised the stated amount for charity within the stated time window.",
    votes: [
      { label: "Atlas",  value: 0.60 },
      { label: "Nova",   value: 0.65 },
      { label: "Orion",  value: 0.58 },
      { label: "Lyra",   value: 0.67 },
      { label: "Zephyr", value: 0.61 },
    ],
    config: { mode: "comparative", marginPercent: 12, threshold: 0.6 },
  },
];
