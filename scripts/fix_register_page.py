"""Fix register page — pass username in signup metadata, remove manual profile insert."""
import pathlib

ROOT = pathlib.Path("C:/GenB/GenLayer Consensus Simulator")
dest = ROOT / "app/(auth)/register/page.tsx"

code = '''\
"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card, CardContent, CardDescription,
  CardFooter, CardHeader, CardTitle,
} from "@/components/ui/card";

export default function RegisterPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [email, setEmail]       = useState("");
  const [password, setPassword] = useState("");
  const [error, setError]       = useState<string | null>(null);
  const [success, setSuccess]   = useState(false);
  const [loading, setLoading]   = useState(false);

  async function handleRegister(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      setLoading(false);
      return;
    }

    const supabase = createClient();

    // Pass username in metadata — the database trigger reads it to create the profile
    const { data, error: signUpError } = await supabase.auth.signUp({
      email,
      password,
      options: {
        emailRedirectTo: `${window.location.origin}/auth/callback`,
        data: { username },
      },
    });

    if (signUpError) {
      setError(signUpError.message);
      setLoading(false);
      return;
    }

    // Profile is created automatically by the on_auth_user_created trigger
    setSuccess(true);
    setLoading(false);

    // If email confirmation is disabled, session is immediately available
    if (data.session) {
      router.push("/");
      router.refresh();
    }
  }

  if (success) {
    return (
      <div className="min-h-screen bg-[#efece4] flex items-center justify-center px-4">
        <Card className="w-full max-w-md text-center p-8">
          <div className="text-4xl mb-4">📬</div>
          <h2 className="text-xl font-semibold text-[#1a1a1a] mb-2">Check your email</h2>
          <p className="text-sm text-[#6b6560]">
            We sent a confirmation link to <strong>{email}</strong>.
            Click it to activate your account.
          </p>
          <div className="mt-6">
            <Link href="/login" className="text-sm text-[#1a1a1a] font-medium hover:underline">
              Back to sign in
            </Link>
          </div>
        </Card>
      </div>
    );
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
                <Input
                  id="username"
                  type="text"
                  placeholder="validator_atlas"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="Min. 8 characters"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
            </CardContent>
            <CardFooter className="flex flex-col gap-3">
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? "Creating account..." : "Create account"}
              </Button>
              <p className="text-sm text-[#6b6560] text-center">
                Already have an account?{" "}
                <Link href="/login" className="text-[#1a1a1a] font-medium hover:underline">
                  Sign in
                </Link>
              </p>
            </CardFooter>
          </form>
        </Card>
      </div>
    </div>
  );
}
'''

dest.write_bytes(code.encode("utf-8"))
print(f"Written: {dest.relative_to(ROOT)}")
