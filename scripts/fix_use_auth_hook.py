"""Rewrite hooks/useAuth.ts to use Firebase instead of Supabase."""
import pathlib

ROOT = pathlib.Path("C:/GenB/GenLayer Consensus Simulator")

p = ROOT / "hooks/useAuth.ts"
p.write_bytes(b'''\
"use client";

import { useEffect } from "react";
import { useAuthStore } from "@/store/authStore";

export function useAuth() {
  const { user, loading, initialized, init } = useAuthStore();

  useEffect(() => {
    if (!initialized) {
      const unsubscribe = init();
      return unsubscribe;
    }
  }, [initialized, init]);

  return { user, loading };
}
''')
print("wrote hooks/useAuth.ts")
