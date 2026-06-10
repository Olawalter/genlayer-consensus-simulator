export interface LLMModel {
  id: string;
  name: string;
  provider: string;
  family: string;
  contextWindow: number;      // tokens
  outputSpeed: number;        // tokens/sec (simulated)
  latencyMs: { min: number; max: number };
  strengths: string[];
  weaknesses: string[];
  acceptBias: number;         // 0-1: tendency to accept subjective claims
  reasoningDepth: number;     // 0-1: how nuanced its reasoning is
  consistencyScore: number;   // 0-1: how reproducible its outputs are
  costPer1kTokens: number;    // USD
  avatar: string;
  color: string;
  description: string;
  usedByValidator: string;
}

export const LLM_MODELS: LLMModel[] = [
  {
    id: "gpt-4o",
    name: "GPT-4o",
    provider: "OpenAI",
    family: "GPT-4",
    contextWindow: 128_000,
    outputSpeed: 62,
    latencyMs: { min: 800,  max: 2200 },
    strengths: ["Instruction following", "Code generation", "Balanced reasoning", "Long context"],
    weaknesses: ["Can be verbose", "Occasionally over-explains"],
    acceptBias: 0.55,
    reasoningDepth: 0.88,
    consistencyScore: 0.85,
    costPer1kTokens: 0.005,
    avatar: "G4",
    color: "emerald",
    description: "OpenAI's most capable and efficient model. Excels at analytical tasks with strong instruction-following. Atlas validator uses GPT-4o for its methodical, data-driven evaluation style.",
    usedByValidator: "Atlas",
  },
  {
    id: "claude-3-5-sonnet",
    name: "Claude 3.5 Sonnet",
    provider: "Anthropic",
    family: "Claude 3.5",
    contextWindow: 200_000,
    outputSpeed: 75,
    latencyMs: { min: 600,  max: 1800 },
    strengths: ["Nuanced reasoning", "Long context", "Safety alignment", "Creative writing"],
    weaknesses: ["Can be overly cautious", "Longer responses"],
    acceptBias: 0.65,
    reasoningDepth: 0.92,
    consistencyScore: 0.88,
    costPer1kTokens: 0.003,
    avatar: "CS",
    color: "orange",
    description: "Anthropic's flagship model with exceptional reasoning and the largest context window. Nova validator leverages Claude's contextual awareness and nuanced interpretations.",
    usedByValidator: "Nova",
  },
  {
    id: "llama-3-70b",
    name: "Llama 3 70B",
    provider: "Meta",
    family: "Llama 3",
    contextWindow: 8_192,
    outputSpeed: 45,
    latencyMs: { min: 1200, max: 3500 },
    strengths: ["Open source", "Cost effective", "Strong reasoning", "Reproducible"],
    weaknesses: ["Smaller context window", "Less instruction-tuned"],
    acceptBias: 0.40,
    reasoningDepth: 0.78,
    consistencyScore: 0.91,
    costPer1kTokens: 0.0009,
    avatar: "L3",
    color: "blue",
    description: "Meta's open-source powerhouse. Highly consistent and reproducible — ideal for strict validation. Orion validator uses Llama 3's conservative, evidence-based approach.",
    usedByValidator: "Orion",
  },
  {
    id: "mistral-large",
    name: "Mistral Large",
    provider: "Mistral AI",
    family: "Mistral",
    contextWindow: 32_000,
    outputSpeed: 80,
    latencyMs: { min: 500,  max: 1500 },
    strengths: ["Fast inference", "European compliance", "Multilingual", "Charitable interpretation"],
    weaknesses: ["Less deep reasoning than GPT-4o", "Smaller community"],
    acceptBias: 0.75,
    reasoningDepth: 0.74,
    consistencyScore: 0.80,
    costPer1kTokens: 0.002,
    avatar: "ML",
    color: "pink",
    description: "Mistral AI's large model balances speed and quality. Known for charitable interpretation of ambiguous claims. Lyra validator uses Mistral's lenient, benefit-of-the-doubt approach.",
    usedByValidator: "Lyra",
  },
  {
    id: "gemini-1.5-pro",
    name: "Gemini 1.5 Pro",
    provider: "Google",
    family: "Gemini 1.5",
    contextWindow: 1_000_000,
    outputSpeed: 68,
    latencyMs: { min: 700,  max: 2000 },
    strengths: ["Massive context window", "Multimodal", "Strong factual grounding", "Balanced"],
    weaknesses: ["Can be inconsistent", "Variable response length"],
    acceptBias: 0.58,
    reasoningDepth: 0.82,
    consistencyScore: 0.79,
    costPer1kTokens: 0.0035,
    avatar: "GP",
    color: "violet",
    description: "Google's most capable model with a 1M token context window. Zephyr validator uses Gemini's balanced, proportional evidence-weighing approach for pragmatic consensus.",
    usedByValidator: "Zephyr",
  },
];

export const MODEL_COLORS: Record<string, { bg: string; text: string; border: string; badge: string }> = {
  emerald: { bg: "bg-emerald-50", text: "text-emerald-700", border: "border-emerald-200", badge: "bg-emerald-100" },
  orange:  { bg: "bg-orange-50",  text: "text-orange-700",  border: "border-orange-200",  badge: "bg-orange-100"  },
  blue:    { bg: "bg-blue-50",    text: "text-blue-700",    border: "border-blue-200",     badge: "bg-blue-100"   },
  pink:    { bg: "bg-pink-50",    text: "text-pink-700",    border: "border-pink-200",     badge: "bg-pink-100"   },
  violet:  { bg: "bg-violet-50",  text: "text-violet-700",  border: "border-violet-200",   badge: "bg-violet-100" },
};
