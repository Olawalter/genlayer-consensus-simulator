"""Remove remaining Supabase references — rewrite dashboard layout and server actions."""
import pathlib, shutil

ROOT = pathlib.Path("C:/GenB/GenLayer Consensus Simulator")

def write(rel: str, code: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(code.encode("utf-8"))
    print(f"  wrote  {rel}")

# ── 1. app/actions/auth.ts — Firebase version ─────────────────────────────────
write("app/actions/auth.ts", """\
"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { cookies } from "next/headers";
import { SESSION_COOKIE } from "@/lib/firebase/auth-helpers";

export async function signOut() {
  const cookieStore = await cookies();
  cookieStore.set(SESSION_COOKIE, "", {
    httpOnly: true,
    secure:   process.env.NODE_ENV === "production",
    sameSite: "lax",
    maxAge:   0,
    path:     "/",
  });
  revalidatePath("/", "layout");
  redirect("/login");
}
""")

# ── 2. app/(dashboard)/layout.tsx — Firebase version ─────────────────────────
write("app/(dashboard)/layout.tsx", """\
import Link from "next/link";
import type { Route } from "next";
import { getServerUser } from "@/lib/firebase/auth-helpers";
import { getUserProfile } from "@/lib/firebase/firestore";
import { signOut } from "@/app/actions/auth";
import { Button } from "@/components/ui/button";

const navLinks: { href: Route; label: string }[] = [
  { href: "/", label: "Home" },
  { href: "/playground", label: "Playground" },
  { href: "/validator-lab", label: "Validators" },
  { href: "/appeals", label: "Appeals" },
  { href: "/equivalence", label: "Equivalence" },
  { href: "/learn", label: "Learn" },
];

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const serverUser = await getServerUser();
  let username = "Explorer";

  if (serverUser) {
    const profile = await getUserProfile(serverUser.uid);
    if (profile) username = profile.username;
  }

  return (
    <div className="min-h-screen bg-[#efece4]">
      <header className="sticky top-0 z-50 border-b border-[#d8d4c8] bg-[#efece4]/90 backdrop-blur-sm">
        <div className="mx-auto max-w-7xl px-6 h-14 flex items-center justify-between">
          <Link href={"/" as Route} className="flex items-center gap-2">
            <div className="h-6 w-6 rounded-md bg-[#2d2a26] flex items-center justify-center">
              <span className="text-[#efece4] text-xs font-bold">GL</span>
            </div>
            <span className="font-semibold text-sm text-[#1a1a1a]">
              Consensus Simulator
            </span>
          </Link>

          <nav className="hidden md:flex items-center gap-5">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="text-sm text-[#6b6560] hover:text-[#1a1a1a] transition-colors"
              >
                {link.label}
              </Link>
            ))}
          </nav>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 rounded-full border border-[#d8d4c8] bg-white/50 px-3 py-1 text-xs text-[#6b6560]">
              <span className="h-1.5 w-1.5 rounded-full bg-green-500" />
              Studio Net
            </div>
            {serverUser ? (
              <div className="flex items-center gap-2">
                <span className="text-xs text-[#6b6560] hidden sm:block">
                  {username}
                </span>
                <form action={signOut}>
                  <Button variant="ghost" size="sm" type="submit" className="text-xs h-8">
                    Sign out
                  </Button>
                </form>
              </div>
            ) : (
              <Link href={"/login" as Route}>
                <Button variant="outline" size="sm" className="text-xs h-8">
                  Sign in
                </Button>
              </Link>
            )}
          </div>
        </div>
      </header>
      <main>{children}</main>
    </div>
  );
}
""")

# ── 3. Delete lib/supabase/ directory ─────────────────────────────────────────
supabase_dir = ROOT / "lib" / "supabase"
if supabase_dir.exists():
    shutil.rmtree(supabase_dir)
    print("  removed lib/supabase/")
else:
    print("  lib/supabase/ already gone")

print("\nDone. Run: python scripts/run_firebase_migration.py  (or just npm run build)")
