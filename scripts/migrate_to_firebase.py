"""Migrate backend from Supabase to Firebase.
Installs firebase package, removes supabase packages,
rewrites all auth/db lib files, middleware, auth pages,
and API routes.
"""
import pathlib, subprocess, sys, json

ROOT = pathlib.Path("C:/GenB/GenLayer Consensus Simulator")

def write(rel: str, code: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(code.encode("utf-8"))
    print(f"  wrote  {rel}")

def run(*args, check=True, capture=False):
    return subprocess.run(
        list(args), cwd=ROOT, check=check,
        capture_output=capture, text=True, shell=True
    )

# ── Firebase config (web app) ────────────────────────────────────────────────
FB = {
    "apiKey":            "AIzaSyDS_chVpGjQ68gWKl9mbFdkonftFlS61vo",
    "authDomain":        "genlayer-consensus-simulator.firebaseapp.com",
    "databaseURL":       "https://genlayer-consensus-simulator-default-rtdb.firebaseio.com",
    "projectId":         "genlayer-consensus-simulator",
    "storageBucket":     "genlayer-consensus-simulator.firebasestorage.app",
    "messagingSenderId": "342879568776",
    "appId":             "1:342879568776:web:17641a97558b57a39e703d",
    "measurementId":     "G-QDP7C3ECLW",
}

# ─────────────────────────────────────────────────────────────────────────────
# 1. Install firebase + firebase-admin, remove supabase
# ─────────────────────────────────────────────────────────────────────────────
print("\n[1/9] Installing Firebase packages...")
run("npm", "install", "firebase", "firebase-admin")

print("[1/9] Removing Supabase packages...")
run("npm", "uninstall", "@supabase/ssr", "@supabase/supabase-js", check=False)

# ─────────────────────────────────────────────────────────────────────────────
# 2. lib/firebase/client.ts
# ─────────────────────────────────────────────────────────────────────────────
print("\n[2/9] Writing Firebase lib files...")
write("lib/firebase/client.ts", f"""\
import {{ initializeApp, getApps, getApp }} from "firebase/app";
import {{ getAuth }} from "firebase/auth";
import {{ getFirestore }} from "firebase/firestore";

const firebaseConfig = {{
  apiKey:            "{FB['apiKey']}",
  authDomain:        "{FB['authDomain']}",
  databaseURL:       "{FB['databaseURL']}",
  projectId:         "{FB['projectId']}",
  storageBucket:     "{FB['storageBucket']}",
  messagingSenderId: "{FB['messagingSenderId']}",
  appId:             "{FB['appId']}",
  measurementId:     "{FB['measurementId']}",
}};

// Prevent re-initializing during hot reload
const app = getApps().length ? getApp() : initializeApp(firebaseConfig);

export const auth = getAuth(app);
export const db   = getFirestore(app);
export default app;
""")

# ─────────────────────────────────────────────────────────────────────────────
# 3. lib/firebase/admin.ts
# ─────────────────────────────────────────────────────────────────────────────
write("lib/firebase/admin.ts", f"""\
import * as admin from "firebase-admin";

// Service account key stored as a JSON string in env var FIREBASE_SERVICE_ACCOUNT_KEY
function getAdminApp() {{
  if (admin.apps.length) return admin.apps[0]!;

  const serviceAccountJson = process.env.FIREBASE_SERVICE_ACCOUNT_KEY;

  if (!serviceAccountJson) {{
    // Dev fallback: use application default credentials or project ID only
    return admin.initializeApp({{
      projectId: "{FB['projectId']}",
    }});
  }}

  try {{
    const serviceAccount = JSON.parse(serviceAccountJson);
    return admin.initializeApp({{
      credential: admin.credential.cert(serviceAccount),
      projectId:  "{FB['projectId']}",
    }});
  }} catch {{
    throw new Error("FIREBASE_SERVICE_ACCOUNT_KEY is not valid JSON");
  }}
}}

export const adminApp  = getAdminApp();
export const adminAuth = admin.auth(adminApp);
export const adminDb   = admin.firestore(adminApp);
""")

# ─────────────────────────────────────────────────────────────────────────────
# 4. lib/firebase/firestore.ts  — typed Firestore helpers
# ─────────────────────────────────────────────────────────────────────────────
write("lib/firebase/firestore.ts", """\
import {
  doc, getDoc, setDoc, updateDoc, deleteDoc,
  collection, query, where, getDocs, addDoc,
  serverTimestamp, type DocumentData,
} from "firebase/firestore";
import { db } from "./client";

// ── User profiles ─────────────────────────────────────────────────────────

export interface UserProfile {
  uid:       string;
  username:  string;
  email:     string;
  role:      "learner" | "admin";
  xp:        number;
  createdAt: unknown; // Firestore Timestamp
}

export async function createUserProfile(
  uid: string,
  data: Omit<UserProfile, "uid" | "createdAt">
): Promise<void> {
  await setDoc(doc(db, "users", uid), {
    ...data,
    uid,
    createdAt: serverTimestamp(),
  });
}

export async function getUserProfile(uid: string): Promise<UserProfile | null> {
  const snap = await getDoc(doc(db, "users", uid));
  return snap.exists() ? (snap.data() as UserProfile) : null;
}

export async function updateUserXp(uid: string, xp: number): Promise<void> {
  await updateDoc(doc(db, "users", uid), { xp });
}

// ── Analytics events ──────────────────────────────────────────────────────

export async function logAnalyticsEvent(
  uid: string | null,
  eventType: string,
  payload: Record<string, unknown>
): Promise<void> {
  await addDoc(collection(db, "analytics_events"), {
    uid,
    eventType,
    payload,
    createdAt: serverTimestamp(),
  });
}

// ── Simulations ────────────────────────────────────────────────────────────

export async function saveSimulation(
  uid: string,
  data: Record<string, unknown>
): Promise<string> {
  const ref = await addDoc(collection(db, "simulations"), {
    ...data,
    uid,
    createdAt: serverTimestamp(),
  });
  return ref.id;
}

export async function getUserSimulations(uid: string): Promise<DocumentData[]> {
  const q = query(collection(db, "simulations"), where("uid", "==", uid));
  const snap = await getDocs(q);
  return snap.docs.map((d) => ({ id: d.id, ...d.data() }));
}
""")

# ─────────────────────────────────────────────────────────────────────────────
# 5. lib/firebase/auth-helpers.ts  — server-side cookie auth
# ─────────────────────────────────────────────────────────────────────────────
write("lib/firebase/auth-helpers.ts", """\
import { cookies } from "next/headers";
import { adminAuth } from "./admin";

export const SESSION_COOKIE = "fb_session";
export const SESSION_MAX_AGE = 60 * 60 * 24 * 14; // 14 days in seconds

/**
 * Exchange a Firebase ID token for a session cookie.
 * Call this from POST /api/auth/session after client-side login.
 */
export async function createSessionCookie(idToken: string): Promise<string> {
  const expiresIn = SESSION_MAX_AGE * 1000; // ms
  return adminAuth.createSessionCookie(idToken, { expiresIn });
}

/**
 * Verify the session cookie stored in the request cookies.
 * Returns the decoded token claims or null if invalid.
 */
export async function verifySessionCookie(
  sessionCookie: string
): Promise<{ uid: string; email?: string } | null> {
  try {
    const decoded = await adminAuth.verifySessionCookie(sessionCookie, true);
    return { uid: decoded.uid, email: decoded.email };
  } catch {
    return null;
  }
}

/**
 * Get the current authenticated user from server-side cookies.
 */
export async function getServerUser(): Promise<{ uid: string; email?: string } | null> {
  const cookieStore = await cookies();
  const session = cookieStore.get(SESSION_COOKIE)?.value;
  if (!session) return null;
  return verifySessionCookie(session);
}
""")

# ─────────────────────────────────────────────────────────────────────────────
# 6. API route: /api/auth/session — create & destroy session cookies
# ─────────────────────────────────────────────────────────────────────────────
write("app/api/auth/session/route.ts", """\
import { NextRequest, NextResponse } from "next/server";
import { createSessionCookie, SESSION_COOKIE, SESSION_MAX_AGE } from "@/lib/firebase/auth-helpers";

// POST /api/auth/session — exchange ID token for session cookie
export async function POST(req: NextRequest) {
  try {
    const { idToken } = await req.json();
    if (!idToken) return NextResponse.json({ error: "idToken required" }, { status: 400 });

    const sessionCookie = await createSessionCookie(idToken);

    const res = NextResponse.json({ status: "ok" });
    res.cookies.set(SESSION_COOKIE, sessionCookie, {
      httpOnly: true,
      secure:   process.env.NODE_ENV === "production",
      sameSite: "lax",
      maxAge:   SESSION_MAX_AGE,
      path:     "/",
    });
    return res;
  } catch (err) {
    console.error("Session creation failed:", err);
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }
}

// DELETE /api/auth/session — clear session cookie on sign-out
export async function DELETE() {
  const res = NextResponse.json({ status: "ok" });
  res.cookies.set(SESSION_COOKIE, "", {
    httpOnly: true,
    secure:   process.env.NODE_ENV === "production",
    sameSite: "lax",
    maxAge:   0,
    path:     "/",
  });
  return res;
}
""")

# ─────────────────────────────────────────────────────────────────────────────
# 7. middleware.ts — Firebase session verification
# ─────────────────────────────────────────────────────────────────────────────
write("middleware.ts", """\
import { type NextRequest, NextResponse } from "next/server";
import { SESSION_COOKIE } from "@/lib/firebase/auth-helpers";

export const runtime = "nodejs";

const PUBLIC_PATHS = ["/login", "/register", "/api/auth/session"];

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Allow public paths, static assets, and API routes through
  const isPublic = PUBLIC_PATHS.some((p) => pathname.startsWith(p))
    || pathname.startsWith("/_next")
    || pathname.startsWith("/favicon");

  if (isPublic) return NextResponse.next();

  const sessionCookie = request.cookies.get(SESSION_COOKIE)?.value;

  if (!sessionCookie) {
    const loginUrl = request.nextUrl.clone();
    loginUrl.pathname = "/login";
    return NextResponse.redirect(loginUrl);
  }

  // Token verification happens in the session API route and server components.
  // Middleware only checks cookie presence for performance.
  // Full verification: use getServerUser() in server components / API routes.
  return NextResponse.next();
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|.*\\\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
""")

# ─────────────────────────────────────────────────────────────────────────────
# 8. store/authStore.ts — client-side Firebase auth state
# ─────────────────────────────────────────────────────────────────────────────
write("store/authStore.ts", """\
"use client";

import { create } from "zustand";
import {
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut as firebaseSignOut,
  onAuthStateChanged,
  type User,
} from "firebase/auth";
import { auth } from "@/lib/firebase/client";
import { createUserProfile, getUserProfile, type UserProfile } from "@/lib/firebase/firestore";

interface AuthStore {
  user:        User | null;
  profile:     UserProfile | null;
  loading:     boolean;
  initialized: boolean;

  signIn:       (email: string, password: string) => Promise<string | null>;
  signUp:       (email: string, password: string, username: string) => Promise<string | null>;
  signOut:      () => Promise<void>;
  refreshProfile: () => Promise<void>;
  init:         () => () => void; // returns unsubscribe
}

async function setSessionCookie(user: User): Promise<void> {
  const idToken = await user.getIdToken();
  await fetch("/api/auth/session", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ idToken }),
  });
}

async function clearSessionCookie(): Promise<void> {
  await fetch("/api/auth/session", { method: "DELETE" });
}

export const useAuthStore = create<AuthStore>((set, get) => ({
  user:        null,
  profile:     null,
  loading:     false,
  initialized: false,

  init: () => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      if (user) {
        const profile = await getUserProfile(user.uid);
        set({ user, profile, initialized: true });
      } else {
        set({ user: null, profile: null, initialized: true });
      }
    });
    return unsubscribe;
  },

  signIn: async (email, password) => {
    set({ loading: true });
    try {
      const cred = await signInWithEmailAndPassword(auth, email, password);
      await setSessionCookie(cred.user);
      const profile = await getUserProfile(cred.user.uid);
      set({ user: cred.user, profile, loading: false });
      return null;
    } catch (err: unknown) {
      set({ loading: false });
      return err instanceof Error ? err.message : "Sign in failed";
    }
  },

  signUp: async (email, password, username) => {
    set({ loading: true });
    try {
      const cred = await createUserWithEmailAndPassword(auth, email, password);
      await createUserProfile(cred.user.uid, {
        username,
        email,
        role: "learner",
        xp: 0,
      });
      await setSessionCookie(cred.user);
      const profile = await getUserProfile(cred.user.uid);
      set({ user: cred.user, profile, loading: false });
      return null;
    } catch (err: unknown) {
      set({ loading: false });
      return err instanceof Error ? err.message : "Sign up failed";
    }
  },

  signOut: async () => {
    await firebaseSignOut(auth);
    await clearSessionCookie();
    set({ user: null, profile: null });
  },

  refreshProfile: async () => {
    const { user } = get();
    if (!user) return;
    const profile = await getUserProfile(user.uid);
    set({ profile });
  },
}));
""")

# ─────────────────────────────────────────────────────────────────────────────
# 9. app/(auth)/register/page.tsx
# ─────────────────────────────────────────────────────────────────────────────
write("app/(auth)/register/page.tsx", """\
"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/authStore";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card, CardContent, CardDescription,
  CardFooter, CardHeader, CardTitle,
} from "@/components/ui/card";

export default function RegisterPage() {
  const router   = useRouter();
  const { signUp } = useAuthStore();

  const [username, setUsername] = useState("");
  const [email,    setEmail]    = useState("");
  const [password, setPassword] = useState("");
  const [error,    setError]    = useState<string | null>(null);
  const [loading,  setLoading]  = useState(false);

  async function handleRegister(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }

    setLoading(true);
    const err = await signUp(email, password, username);
    setLoading(false);

    if (err) {
      // Make Firebase error messages user-friendly
      if (err.includes("email-already-in-use"))  setError("An account with this email already exists.");
      else if (err.includes("invalid-email"))    setError("Please enter a valid email address.");
      else if (err.includes("weak-password"))    setError("Password is too weak. Use at least 8 characters.");
      else setError(err);
      return;
    }

    router.push("/");
    router.refresh();
  }

  return (
    <div className="min-h-screen bg-[#efece4] flex items-center justify-center px-4">
      <div className="w-full max-w-md space-y-6">
        <div className="text-center space-y-2">
          <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-[#2d2a26]">
            <span className="text-[#efece4] text-lg font-bold">GL</span>
          </div>
          <h1 className="text-2xl font-bold text-[#1a1a1a]">Create an account</h1>
          <p className="text-sm text-[#6b6560]">Start exploring Consensus Simulator</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Sign up</CardTitle>
            <CardDescription>Free access · No credit card required</CardDescription>
          </CardHeader>
          <form onSubmit={handleRegister}>
            <CardContent className="space-y-4">
              {error && (
                <div className="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                  {error}
                </div>
              )}
              <div className="space-y-2">
                <Label htmlFor="username">Username</Label>
                <Input id="username" type="text" placeholder="validator_atlas"
                  value={username} onChange={(e) => setUsername(e.target.value)} required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input id="email" type="email" placeholder="you@example.com"
                  value={email} onChange={(e) => setEmail(e.target.value)} required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input id="password" type="password" placeholder="Min. 8 characters"
                  value={password} onChange={(e) => setPassword(e.target.value)} required />
              </div>
            </CardContent>
            <CardFooter className="flex flex-col gap-3">
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? "Creating account..." : "Create account"}
              </Button>
              <p className="text-sm text-[#6b6560] text-center">
                Already have an account?{" "}
                <Link href="/login" className="text-[#1a1a1a] font-medium hover:underline">Sign in</Link>
              </p>
            </CardFooter>
          </form>
        </Card>
      </div>
    </div>
  );
}
""")

# ─────────────────────────────────────────────────────────────────────────────
# 10. app/(auth)/login/page.tsx
# ─────────────────────────────────────────────────────────────────────────────
write("app/(auth)/login/page.tsx", """\
"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/authStore";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card, CardContent, CardDescription,
  CardFooter, CardHeader, CardTitle,
} from "@/components/ui/card";

export default function LoginPage() {
  const router  = useRouter();
  const { signIn } = useAuthStore();

  const [email,   setEmail]   = useState("");
  const [password,setPassword]= useState("");
  const [error,   setError]   = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    const err = await signIn(email, password);
    setLoading(false);

    if (err) {
      if (err.includes("user-not-found") || err.includes("wrong-password") || err.includes("invalid-credential"))
        setError("Invalid email or password.");
      else if (err.includes("too-many-requests"))
        setError("Too many attempts. Please wait a moment and try again.");
      else setError(err);
      return;
    }

    router.push("/");
    router.refresh();
  }

  return (
    <div className="min-h-screen bg-[#efece4] flex items-center justify-center px-4">
      <div className="w-full max-w-md space-y-6">
        <div className="text-center space-y-2">
          <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-[#2d2a26]">
            <span className="text-[#efece4] text-lg font-bold">GL</span>
          </div>
          <h1 className="text-2xl font-bold text-[#1a1a1a]">Welcome back</h1>
          <p className="text-sm text-[#6b6560]">Sign in to your account</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Sign in</CardTitle>
            <CardDescription>Enter your email and password</CardDescription>
          </CardHeader>
          <form onSubmit={handleLogin}>
            <CardContent className="space-y-4">
              {error && (
                <div className="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                  {error}
                </div>
              )}
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input id="email" type="email" placeholder="you@example.com"
                  value={email} onChange={(e) => setEmail(e.target.value)} required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input id="password" type="password" placeholder="Your password"
                  value={password} onChange={(e) => setPassword(e.target.value)} required />
              </div>
            </CardContent>
            <CardFooter className="flex flex-col gap-3">
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? "Signing in..." : "Sign in"}
              </Button>
              <p className="text-sm text-[#6b6560] text-center">
                Don&apos;t have an account?{" "}
                <Link href="/register" className="text-[#1a1a1a] font-medium hover:underline">Sign up</Link>
              </p>
            </CardFooter>
          </form>
        </Card>
      </div>
    </div>
  );
}
""")

# ─────────────────────────────────────────────────────────────────────────────
# 11. Remove old Supabase auth callback — replace with simple redirect
# ─────────────────────────────────────────────────────────────────────────────
write("app/auth/callback/route.ts", """\
import { NextResponse } from "next/server";

// Firebase doesn't use OAuth callbacks for email/password auth.
// This route handles any legacy redirects by sending users to the dashboard.
export async function GET() {
  return NextResponse.redirect(
    new URL("/", process.env.NEXT_PUBLIC_APP_URL ?? "http://localhost:3000")
  );
}
""")

# ─────────────────────────────────────────────────────────────────────────────
# 12. Update .env.local
# ─────────────────────────────────────────────────────────────────────────────
env_content = f"""\
# -- Firebase (client) --------------------------------------------------------
NEXT_PUBLIC_FIREBASE_API_KEY={FB['apiKey']}
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN={FB['authDomain']}
NEXT_PUBLIC_FIREBASE_DATABASE_URL={FB['databaseURL']}
NEXT_PUBLIC_FIREBASE_PROJECT_ID={FB['projectId']}
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET={FB['storageBucket']}
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID={FB['messagingSenderId']}
NEXT_PUBLIC_FIREBASE_APP_ID={FB['appId']}
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID={FB['measurementId']}

# -- Firebase Admin (server) --------------------------------------------------
# Paste the entire service account JSON as a single-line string
FIREBASE_SERVICE_ACCOUNT_KEY=PASTE_SERVICE_ACCOUNT_JSON_HERE

# -- App ----------------------------------------------------------------------
NEXT_PUBLIC_APP_URL=https://genlayer-consensus-simulator.vercel.app
NEXTAUTH_SECRET=WWFHbAXsnOGAPgu6k3W7Ig3AsdDSfgnfBCqxvC/mSmk=
"""
(ROOT / ".env.local").write_bytes(env_content.encode("utf-8"))
print("  wrote  .env.local")

# ─────────────────────────────────────────────────────────────────────────────
# 13. Build
# ─────────────────────────────────────────────────────────────────────────────
print("\n[9/9] Running production build...")
result = subprocess.run(
    ["npm", "run", "build"], cwd=ROOT, shell=True,
    capture_output=True, text=True
)
out = result.stdout + result.stderr
print(out[-5000:] if len(out) > 5000 else out)
if result.returncode != 0:
    print("\nBUILD FAILED — see errors above")
    sys.exit(1)
print("\nBUILD PASSED")
