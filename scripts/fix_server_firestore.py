"""Fix server-side Firestore call in dashboard layout.
The layout is a Server Component — it must use firebase-admin (adminDb),
not the firebase client SDK which requires a browser runtime.
"""
import pathlib

ROOT = pathlib.Path("C:/GenB/GenLayer Consensus Simulator")

def write(rel, code):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(code.encode("utf-8"))
    print(f"  wrote  {rel}")

# ── 1. Add admin-side getUserProfile to lib/firebase/admin.ts ─────────────────
write("lib/firebase/admin.ts", """\
import * as admin from "firebase-admin";

function getAdminApp() {
  if (admin.apps.length) return admin.apps[0]!;

  const serviceAccountJson = process.env.FIREBASE_SERVICE_ACCOUNT_KEY;

  if (!serviceAccountJson || serviceAccountJson === "PASTE_SERVICE_ACCOUNT_JSON_HERE") {
    return admin.initializeApp({
      projectId: "genlayer-consensus-simulator",
    });
  }

  try {
    const serviceAccount = JSON.parse(serviceAccountJson);
    return admin.initializeApp({
      credential: admin.credential.cert(serviceAccount),
      projectId:  "genlayer-consensus-simulator",
    });
  } catch {
    throw new Error("FIREBASE_SERVICE_ACCOUNT_KEY is not valid JSON");
  }
}

export const adminApp  = getAdminApp();
export const adminAuth = admin.auth(adminApp);
export const adminDb   = admin.firestore(adminApp);

// Server-side profile lookup — uses Admin SDK, bypasses security rules
export async function getAdminUserProfile(
  uid: string
): Promise<{ uid: string; username: string; email: string; role: string; xp: number } | null> {
  const snap = await adminDb.collection("users").doc(uid).get();
  if (!snap.exists) return null;
  return snap.data() as { uid: string; username: string; email: string; role: string; xp: number };
}
""")

# ── 2. Fix dashboard layout to use getAdminUserProfile ───────────────────────
write("app/(dashboard)/layout.tsx", """\
import Link from "next/link";
import type { Route } from "next";
import { getServerUser } from "@/lib/firebase/auth-helpers";
import { getAdminUserProfile } from "@/lib/firebase/admin";
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
    const profile = await getAdminUserProfile(serverUser.uid);
    if (profile?.username) username = profile.username;
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

print("Done. Run: npm run build")
