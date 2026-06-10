import { sleep } from "@/lib/utils";
import type { LLMModel } from "./models";

export interface LLMResponse {
  modelId: string;
  vote: "ACCEPT" | "REJECT" | "UNCERTAIN";
  confidence: number;
  reasoning: string;
  latencyMs: number;
  tokensUsed: number;
  costUsd: number;
}

const RESPONSE_TEMPLATES: Record<string, (claim: string, vote: string) => string> = {
  "gpt-4o": (claim, vote) => {
    if (vote === "ACCEPT")
      return `Analysing the claim: "${claim.slice(0, 70)}…"

Key evaluation points:
1. The claim is specific and verifiable
2. No logical inconsistencies detected
3. Aligns with standard industry expectations

Verdict: The claim satisfies the required criteria for acceptance.`;
    if (vote === "REJECT")
      return `Evaluating: "${claim.slice(0, 70)}…"

Issues identified:
1. Insufficient verifiable detail
2. Ambiguous success criteria
3. Claim cannot be independently corroborated

Verdict: Rejection recommended pending additional evidence.`;
    return `Assessing: "${claim.slice(0, 70)}…"

Mixed signals detected:
• Some criteria are satisfied
• Others remain ambiguous or unverified

Verdict: Insufficient certainty to render a definitive verdict.`;
  },
  "claude-3-5-sonnet": (claim, vote) => {
    if (vote === "ACCEPT")
      return `I've carefully considered "${claim.slice(0, 70)}…" in its full context.

The intent behind this claim appears genuine. The language used is consistent with authentic performance and the stated outcomes are plausible given the circumstances described. I find the claim credible.

**Assessment:** ACCEPT — the claim meets the reasonable standard of verification.`;
    if (vote === "REJECT")
      return `After thoughtful consideration of "${claim.slice(0, 70)}…", I have concerns.

While I want to give the benefit of the doubt, several elements of this claim raise questions that can't be resolved through charitable interpretation alone. The gap between stated and verifiable outcomes is too significant.

**Assessment:** REJECT — the claim falls short of the required evidential standard.`;
    return `"${claim.slice(0, 70)}…" presents a genuinely difficult case.

I can construct reasonable arguments for both acceptance and rejection. The claim sits precisely at the intersection of plausible and unverifiable. Without additional context, I cannot in good conscience commit to either outcome.

**Assessment:** UNCERTAIN — further evidence is needed.`;
  },
  "llama-3-70b": (claim, vote) => {
    if (vote === "ACCEPT")
      return `CLAIM: "${claim.slice(0, 70)}…"
RESULT: ACCEPT

RATIONALE: After strict verification against defined criteria, this claim meets the required evidentiary threshold. All verifiable components pass scrutiny. No contradictory evidence found.`;
    if (vote === "REJECT")
      return `CLAIM: "${claim.slice(0, 70)}…"
RESULT: REJECT

RATIONALE: Strict evaluation reveals the claim does not meet the required standard of evidence. Critical verification criteria are not satisfied. The claim lacks the specificity and corroboration required for acceptance.`;
    return `CLAIM: "${claim.slice(0, 70)}…"
RESULT: UNCERTAIN

RATIONALE: The claim sits at the boundary of the acceptance threshold. Strict criteria cannot be definitively satisfied or rejected based on available information.`;
  },
  "mistral-large": (claim, vote) => {
    if (vote === "ACCEPT")
      return `Looking at "${claim.slice(0, 70)}…" — this is plausible and the description is consistent with a legitimate outcome. I'm giving the benefit of the doubt here. The claim is reasonable and I see no red flags that would warrant rejection. Accept.`;
    if (vote === "REJECT")
      return `Even being charitable, "${claim.slice(0, 70)}…" has too many unresolved questions. The core premise doesn't hold up on closer inspection. Despite my inclination toward leniency, I can't in good faith accept a claim with these inconsistencies. Reject.`;
    return `"${claim.slice(0, 70)}…" — I want to accept this, but something's not quite right. The claim is borderline. I'll flag as uncertain rather than force a verdict in either direction.`;
  },
  "gemini-1.5-pro": (claim, vote) => {
    if (vote === "ACCEPT")
      return `Balanced assessment of "${claim.slice(0, 70)}…":

**Pro-acceptance factors:** Specific claim, reasonable scope, language consistent with genuine performance.
**Counter-considerations:** Minor ambiguities present but not disqualifying.

**Weighted conclusion:** The evidence balance tips toward acceptance (confidence: proportional to available data).`;
    if (vote === "REJECT")
      return `Balanced assessment of "${claim.slice(0, 70)}…":

**Pro-acceptance factors:** Some elements plausible.
**Counter-considerations:** Key verification criteria unmet; ambiguity exceeds acceptable threshold; evidence weight is insufficient.

**Weighted conclusion:** Rejection is proportionally supported by the evidence.`;
    return `Balanced assessment of "${claim.slice(0, 70)}…":

**Evidence for:** Some plausible elements.
**Evidence against:** Some problematic elements.
**Uncertainty factor:** High — the evidence is approximately equal on both sides.

**Weighted conclusion:** Uncertain verdict; proportional to the genuine ambiguity in the claim.`;
  },
};

function generateVote(model: LLMModel, claim: string): { vote: "ACCEPT" | "REJECT" | "UNCERTAIN"; confidence: number } {
  const hash = Array.from(claim + model.id).reduce((a, c) => a + c.charCodeAt(0), 0);
  const rand = ((hash * 7919 + 104729) % 999983) / 999983;

  const bias    = model.acceptBias;
  const margin  = 0.15;

  let vote: "ACCEPT" | "REJECT" | "UNCERTAIN";
  let confidence: number;

  if (rand > bias + margin / 2) {
    vote = "ACCEPT";
    confidence = model.consistencyScore * 0.85 + (rand - bias) * 0.2;
  } else if (rand < bias - margin / 2) {
    vote = "REJECT";
    confidence = model.consistencyScore * 0.85 + (bias - rand) * 0.2;
  } else {
    vote = "UNCERTAIN";
    confidence = model.consistencyScore * 0.60;
  }

  return { vote, confidence: Math.min(0.98, Math.max(0.51, confidence)) };
}

export async function simulateLLMResponse(
  model: LLMModel,
  claim: string,
  onStart: () => void
): Promise<LLMResponse> {
  onStart();

  // Simulate latency
  const latencyMs = model.latencyMs.min + Math.random() * (model.latencyMs.max - model.latencyMs.min);
  await sleep(Math.round(latencyMs));

  const { vote, confidence } = generateVote(model, claim);
  const template = RESPONSE_TEMPLATES[model.id] ?? RESPONSE_TEMPLATES["gpt-4o"];
  const reasoning = template(claim, vote);

  const tokensUsed = Math.floor(150 + Math.random() * 300);
  const costUsd    = (tokensUsed / 1000) * model.costPer1kTokens;

  return {
    modelId: model.id,
    vote,
    confidence,
    reasoning,
    latencyMs: Math.round(latencyMs),
    tokensUsed,
    costUsd,
  };
}

export async function runLLMComparison(
  models: LLMModel[],
  claim: string,
  onUpdate: (responses: Partial<Record<string, LLMResponse>>, loadingIds: string[]) => void
): Promise<Record<string, LLMResponse>> {
  const responses: Partial<Record<string, LLMResponse>> = {};
  let loadingIds = [...models.map((m) => m.id)];
  onUpdate({ ...responses }, [...loadingIds]);

  // Run all models in parallel
  await Promise.all(
    models.map(async (model) => {
      const resp = await simulateLLMResponse(model, claim, () => {});
      responses[model.id] = resp;
      loadingIds = loadingIds.filter((id) => id !== model.id);
      onUpdate({ ...responses }, [...loadingIds]);
    })
  );

  return responses as Record<string, LLMResponse>;
}
