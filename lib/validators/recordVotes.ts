/**
 * Bridge: after a simulation finishes, persist each validator's vote
 * into the ValidatorStore so the Validator Lab history tab stays current.
 *
 * Called from the playground page after runSimulation() resolves.
 */
import type { SimulationRun } from "@/services/simulationService";
import { useValidatorStore } from "@/store/validatorStore";

export function recordSimulationVotes(run: SimulationRun): void {
  const { addVoteRecord, validators } = useValidatorStore.getState();

  for (const lv of run.validators) {
    if (lv.status !== "voted" || !lv.vote) continue;

    // Match by name (personas are seeded as default_0..4)
    const storeValidator = validators.find((sv) => sv.name === lv.name);
    if (!storeValidator) continue;

    addVoteRecord(storeValidator.id, {
      claim:        run.claim,
      category:     run.category,
      vote:         lv.vote,
      confidence:   lv.confidence ?? 0,
      reasoning:    lv.reasoning ?? "",
      simulationId: run.id,
    });
  }
}
