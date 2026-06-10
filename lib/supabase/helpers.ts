/**
 * Typed helper wrappers for Supabase inserts.
 *
 * supabase-js v2 uses a complex select-query-parser generic chain that
 * requires CLI-generated types to resolve correctly. Until `supabase gen types`
 * is run after the project is connected, these helpers use a minimal cast
 * to keep full TypeScript safety in all read/select operations.
 */
import type { Database } from "@/types/supabase";

type ProfileInsert = Database["public"]["Tables"]["profiles"]["Insert"];

// Use a structural type that matches any supabase client regardless of generic params
type AnySupabaseClient = {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  from: (table: string) => any;
};

export async function insertProfile(
  supabase: AnySupabaseClient,
  values: ProfileInsert
): Promise<{ error: { message: string } | null }> {
  return supabase.from("profiles").insert(values);
}
