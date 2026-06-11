import { createClient, createAccount } from "genlayer-js";
import { studionet } from "genlayer-js/chains";

// Studio Net runs locally at localhost:4000
// All calls are client-side (browser → localhost) — never call from server components
export function getGenLayerClient() {
  const privateKey = process.env.NEXT_PUBLIC_GENLAYER_PRIVATE_KEY as `0x${string}`;
  if (!privateKey) throw new Error("NEXT_PUBLIC_GENLAYER_PRIVATE_KEY is not set");

  const account = createAccount(privateKey);
  return createClient({
    chain: studionet,
    account,
  });
}

// Singleton for client-side use
let _client: ReturnType<typeof getGenLayerClient> | null = null;

export function getClient() {
  if (!_client) _client = getGenLayerClient();
  return _client;
}
