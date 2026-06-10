export type ValidatorPersona = "strict" | "lenient" | "analytical" | "creative" | "balanced";

export interface ValidatorPersonaConfig {
  name: string;
  model: string;
  persona: ValidatorPersona;
  acceptThreshold: number;   // 0–1: probability of ACCEPT on neutral claims
  uncertaintyRange: number;  // 0–1: how wide the uncertain zone is
  confidenceBase: number;    // base confidence level
  color: string;
  avatar: string;
  description: string;
  reasoningStyle: string;
}

export const VALIDATOR_PERSONAS: ValidatorPersonaConfig[] = [
  {
    name: "Atlas",
    model: "gpt-4o",
    persona: "analytical",
    acceptThreshold: 0.55,
    uncertaintyRange: 0.15,
    confidenceBase: 0.82,
    color: "indigo",
    avatar: "AT",
    description: "Methodical and data-driven. Evaluates claims against objective criteria.",
    reasoningStyle: "analytical",
  },
  {
    name: "Nova",
    model: "claude-3-5-sonnet",
    persona: "creative",
    acceptThreshold: 0.65,
    uncertaintyRange: 0.2,
    confidenceBase: 0.74,
    color: "pink",
    avatar: "NV",
    description: "Contextual and nuanced. Considers intent and broader implications.",
    reasoningStyle: "contextual",
  },
  {
    name: "Orion",
    model: "llama-3-70b",
    persona: "strict",
    acceptThreshold: 0.40,
    uncertaintyRange: 0.1,
    confidenceBase: 0.91,
    color: "red",
    avatar: "OR",
    description: "Conservative and precise. Requires strong evidence before accepting.",
    reasoningStyle: "strict",
  },
  {
    name: "Lyra",
    model: "mistral-large",
    persona: "lenient",
    acceptThreshold: 0.75,
    uncertaintyRange: 0.2,
    confidenceBase: 0.68,
    color: "emerald",
    avatar: "LY",
    description: "Generous and charitable. Gives benefit of the doubt when claims are plausible.",
    reasoningStyle: "lenient",
  },
  {
    name: "Zephyr",
    model: "gemini-1.5-pro",
    persona: "balanced",
    acceptThreshold: 0.58,
    uncertaintyRange: 0.18,
    confidenceBase: 0.77,
    color: "amber",
    avatar: "ZP",
    description: "Balanced and pragmatic. Weighs evidence proportionally across all factors.",
    reasoningStyle: "balanced",
  },
];

export const PERSONA_COLORS: Record<string, { bg: string; text: string; border: string; glow: string }> = {
  indigo:  { bg: "bg-indigo-50",  text: "text-indigo-700",  border: "border-indigo-200", glow: "shadow-indigo-200" },
  pink:    { bg: "bg-pink-50",    text: "text-pink-700",    border: "border-pink-200",   glow: "shadow-pink-200" },
  red:     { bg: "bg-red-50",     text: "text-red-700",     border: "border-red-200",    glow: "shadow-red-200" },
  emerald: { bg: "bg-emerald-50", text: "text-emerald-700", border: "border-emerald-200",glow: "shadow-emerald-200" },
  amber:   { bg: "bg-amber-50",   text: "text-amber-700",   border: "border-amber-200",  glow: "shadow-amber-200" },
};
