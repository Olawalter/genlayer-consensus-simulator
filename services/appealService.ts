import { VALIDATOR_PERSONAS } from "@/lib/validators/personas";
import { computeEquivalence } from "@/lib/validators/equivalence";
import { sleep } from "@/lib/utils";
import { useAppealStore, type AppealRound } from "@/store/appealStore";
import type { SimulationRun, LiveValidator } from "@/services/simulationService";
import type { ValidatorVote } from "@/types/validator";

// Reasoning templates for appeal round validators
const APPEAL_REASONING: Record<string, (claim: string, vote: string, round: number) => string> = {
  ACCEPT: (claim, _v, round) =>
    round === 1
      ? `Re-evaluating "${claim.slice(0, 55)}…" with a fresh perspective. The core claim stands up to scrutiny — I find sufficient grounds for acceptance on appeal.`
      : `After extended deliberation across ${round} rounds, the weight of evidence still supports acceptance. My position is unchanged.`,
  REJECT: (claim, _v, round) =>
    round === 1
      ? `Reviewing "${claim.slice(0, 55)}…" as an appeal validator. The original rejection concerns remain unaddressed. I concur: this claim does not meet the required standard.`
      : `This is round ${round} of review. The fundamental issues with this claim persist. Rejection stands.`,
  UNCERTAIN: (claim, _v, round) =>
    `Even on appeal (round ${round}), "${claim.slice(0, 55)}…" remains genuinely ambiguous. I cannot commit to either outcome without additional context.`,
};

function generateAppealVote(
  personaIdx: number,
  claim: string,
  round: number,
  seed: string
): { vote: "ACCEPT" | "REJECT" | "UNCERTAIN"; confidence: number; reasoning: string } {
  const persona = VALIDATOR_PERSONAS[personaIdx % VALIDATOR_PERSONAS.length];
  const hash = Array.from(claim + persona.name + seed + round).reduce((a, c) => a + c.charCodeAt(0), 0);
  const rand = ((hash * 6271 + 31337) % 233280) / 233280;

  const band = persona.uncertaintyRange;
  const thr  = persona.acceptThreshold;

  let vote: "ACCEPT" | "REJECT" | "UNCERTAIN";
  let confidence: number;

  if (rand > thr + band / 2) {
    vote = "ACCEPT";
    confidence = Math.min(0.97, persona.confidenceBase + (rand - thr) * 0.15);
  } else if (rand < thr - band / 2) {
    vote = "REJECT";
    confidence = Math.min(0.97, persona.confidenceBase + (thr - rand) * 0.15);
  } else {
    vote = "UNCERTAIN";
    confidence = persona.confidenceBase * 0.65;
  }

  confidence = Math.max(0.52, confidence);
  const reasoning = APPEAL_REASONING[vote]?.(claim, vote, round) ?? "";
  return { vote, confidence, reasoning };
}

export interface AppealValidatorUpdate {
  id: string;
  name: string;
  model: string;
  avatar: string;
  color: string;
  isOriginal: boolean;
  status: "waiting" | "thinking" | "voted";
  vote: "ACCEPT" | "REJECT" | "UNCERTAIN" | null;
  confidence: number | null;
  reasoning: string | null;
  round: number;
}

export async function executeAppealRound(
  originalRun: SimulationRun,
  reason: string,
  roundNumber: number,
  onUpdate: (validators: AppealValidatorUpdate[]) => void
): Promise<AppealRound> {
  const startTime = Date.now();

  // Original validators carry over their votes (frozen)
  const originalValidators: AppealValidatorUpdate[] = originalRun.validators
    .filter((v) => v.vote !== null)
    .map((v) => ({
      id: v.id,
      name: v.name,
      model: v.model,
      avatar: v.avatar,
      color: v.color,
      isOriginal: true,
      status: "voted" as const,
      vote: v.vote,
      confidence: v.confidence,
      reasoning: v.reasoning,
      round: 1,
    }));

  // Appeal validators — expand by 3 each round (capped at 5 extra)
  const extraCount = Math.min(3 + (roundNumber - 2) * 2, 5);
  const appealValidators: AppealValidatorUpdate[] = Array.from({ length: extraCount }, (_, i) => {
    const p = VALIDATOR_PERSONAS[(i + roundNumber) % VALIDATOR_PERSONAS.length];
    return {
      id: `appeal_r${roundNumber}_v${i}`,
      name: `${p.name} (R${roundNumber})`,
      model: p.model,
      avatar: p.avatar,
      color: p.color,
      isOriginal: false,
      status: "waiting" as const,
      vote: null,
      confidence: null,
      reasoning: null,
      round: roundNumber,
    };
  });

  const allValidators = [...originalValidators, ...appealValidators];
  onUpdate([...allValidators]);

  // Stagger appeal votes
  for (let i = 0; i < appealValidators.length; i++) {
    await sleep(350);
    allValidators[originalValidators.length + i] = {
      ...allValidators[originalValidators.length + i],
      status: "thinking",
    };
    onUpdate([...allValidators]);

    await sleep(900 + i * 400);

    const result = generateAppealVote(i + roundNumber, originalRun.claim, roundNumber, reason);
    allValidators[originalValidators.length + i] = {
      ...allValidators[originalValidators.length + i],
      status: "voted",
      ...result,
    };
    onUpdate([...allValidators]);
  }

  // Compute new equivalence over ALL votes (original + appeal)
  const allVotes: ValidatorVote[] = allValidators
    .filter((v) => v.vote !== null)
    .map((v) => ({
      validatorId: v.id,
      simulationId: originalRun.id,
      role: "validator" as const,
      vote: v.vote!,
      confidence: v.confidence!,
      reasoning: v.reasoning ?? "",
      equivalenceScore: 0,
    }));

  const equivalenceResult = computeEquivalence(allVotes);

  const round: AppealRound = {
    roundNumber,
    validatorCount: allVotes.length,
    votes: allValidators
      .filter((v) => v.vote !== null)
      .map((v) => ({ name: v.name, vote: v.vote!, confidence: v.confidence! })),
    equivalenceResult,
    outcome: equivalenceResult.outcome,
    durationMs: Date.now() - startTime,
  };

  // Persist to store
  const { addRound, resolveAppeal, activeAppealId } = useAppealStore.getState();
  if (activeAppealId) {
    addRound(activeAppealId, round);
    if (equivalenceResult.outcome !== "APPEAL_TRIGGERED") {
      resolveAppeal(activeAppealId, equivalenceResult.outcome === "ACCEPTED" ? "ACCEPTED" : "REJECTED");
    }
  }

  return round;
}
