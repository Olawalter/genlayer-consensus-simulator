"""Phase 3: Supabase clients, middleware, auth pages, shadcn UI components."""
import pathlib

ROOT = pathlib.Path("C:/GenB/GenLayer Consensus Simulator")


def w(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"  WROTE  {rel}")


# ---------------------------------------------------------------------------
# 1. shadcn-style UI primitives (no CLI needed – written manually)
# ---------------------------------------------------------------------------

w("components/ui/button.tsx", '''\
import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-[#2d2a26] text-[#efece4] hover:bg-[#2d2a26]/90",
        destructive: "bg-red-600 text-white hover:bg-red-700",
        outline: "border border-[#d8d4c8] bg-transparent hover:bg-[#e8e4da] hover:text-[#1a1a1a]",
        secondary: "bg-[#e8e4da] text-[#1a1a1a] hover:bg-[#d8d4c8]",
        ghost: "hover:bg-[#e8e4da] hover:text-[#1a1a1a]",
        link: "text-[#2d2a26] underline-offset-4 hover:underline",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: { variant: "default", size: "default" },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp className={cn(buttonVariants({ variant, size, className }))} ref={ref} {...props} />
    );
  }
);
Button.displayName = "Button";

export { Button, buttonVariants };
''')

w("components/ui/input.tsx", '''\
import * as React from "react";
import { cn } from "@/lib/utils";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => (
    <input
      type={type}
      className={cn(
        "flex h-10 w-full rounded-md border border-[#d8d4c8] bg-white/60 px-3 py-2 text-sm ring-offset-background",
        "file:border-0 file:bg-transparent file:text-sm file:font-medium",
        "placeholder:text-[#6b6560]",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
        "disabled:cursor-not-allowed disabled:opacity-50",
        className
      )}
      ref={ref}
      {...props}
    />
  )
);
Input.displayName = "Input";

export { Input };
''')

w("components/ui/label.tsx", '''\
import * as React from "react";
import * as LabelPrimitive from "@radix-ui/react-label";
import { cn } from "@/lib/utils";

const Label = React.forwardRef<
  React.ElementRef<typeof LabelPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof LabelPrimitive.Root>
>(({ className, ...props }, ref) => (
  <LabelPrimitive.Root
    ref={ref}
    className={cn(
      "text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70",
      className
    )}
    {...props}
  />
));
Label.displayName = LabelPrimitive.Root.displayName;

export { Label };
''')

w("components/ui/card.tsx", '''\
import * as React from "react";
import { cn } from "@/lib/utils";

const Card = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn("rounded-xl border border-[#d8d4c8] bg-white/60 backdrop-blur-sm shadow-sm", className)}
      {...props}
    />
  )
);
Card.displayName = "Card";

const CardHeader = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn("flex flex-col space-y-1.5 p-6", className)} {...props} />
  )
);
CardHeader.displayName = "CardHeader";

const CardTitle = React.forwardRef<HTMLParagraphElement, React.HTMLAttributes<HTMLHeadingElement>>(
  ({ className, ...props }, ref) => (
    <h3 ref={ref} className={cn("text-xl font-semibold leading-none tracking-tight", className)} {...props} />
  )
);
CardTitle.displayName = "CardTitle";

const CardDescription = React.forwardRef<HTMLParagraphElement, React.HTMLAttributes<HTMLParagraphElement>>(
  ({ className, ...props }, ref) => (
    <p ref={ref} className={cn("text-sm text-[#6b6560]", className)} {...props} />
  )
);
CardDescription.displayName = "CardDescription";

const CardContent = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn("p-6 pt-0", className)} {...props} />
  )
);
CardContent.displayName = "CardContent";

const CardFooter = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn("flex items-center p-6 pt-0", className)} {...props} />
  )
);
CardFooter.displayName = "CardFooter";

export { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter };
''')

w("components/ui/separator.tsx", '''\
import * as React from "react";
import * as SeparatorPrimitive from "@radix-ui/react-separator";
import { cn } from "@/lib/utils";

const Separator = React.forwardRef<
  React.ElementRef<typeof SeparatorPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof SeparatorPrimitive.Root>
>(({ className, orientation = "horizontal", decorative = true, ...props }, ref) => (
  <SeparatorPrimitive.Root
    ref={ref}
    decorative={decorative}
    orientation={orientation}
    className={cn(
      "shrink-0 bg-[#d8d4c8]",
      orientation === "horizontal" ? "h-[1px] w-full" : "h-full w-[1px]",
      className
    )}
    {...props}
  />
));
Separator.displayName = SeparatorPrimitive.Root.displayName;

export { Separator };
''')

w("components/ui/badge.tsx", '''\
import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors",
  {
    variants: {
      variant: {
        default: "border-transparent bg-[#2d2a26] text-[#efece4]",
        secondary: "border-transparent bg-[#e8e4da] text-[#1a1a1a]",
        destructive: "border-transparent bg-red-600 text-white",
        outline: "border-[#d8d4c8] text-[#1a1a1a]",
        accept: "border-green-200 bg-green-50 text-green-700",
        reject: "border-red-200 bg-red-50 text-red-700",
        uncertain: "border-amber-200 bg-amber-50 text-amber-700",
        leader: "border-indigo-200 bg-indigo-50 text-indigo-700",
        appealed: "border-purple-200 bg-purple-50 text-purple-700",
      },
    },
    defaultVariants: { variant: "default" },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };
''')

w("components/ui/avatar.tsx", '''\
import * as React from "react";
import * as AvatarPrimitive from "@radix-ui/react-avatar";
import { cn } from "@/lib/utils";

const Avatar = React.forwardRef<
  React.ElementRef<typeof AvatarPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof AvatarPrimitive.Root>
>(({ className, ...props }, ref) => (
  <AvatarPrimitive.Root
    ref={ref}
    className={cn("relative flex h-10 w-10 shrink-0 overflow-hidden rounded-full", className)}
    {...props}
  />
));
Avatar.displayName = AvatarPrimitive.Root.displayName;

const AvatarImage = React.forwardRef<
  React.ElementRef<typeof AvatarPrimitive.Image>,
  React.ComponentPropsWithoutRef<typeof AvatarPrimitive.Image>
>(({ className, ...props }, ref) => (
  <AvatarPrimitive.Image ref={ref} className={cn("aspect-square h-full w-full", className)} {...props} />
));
AvatarImage.displayName = AvatarPrimitive.Image.displayName;

const AvatarFallback = React.forwardRef<
  React.ElementRef<typeof AvatarPrimitive.Fallback>,
  React.ComponentPropsWithoutRef<typeof AvatarPrimitive.Fallback>
>(({ className, ...props }, ref) => (
  <AvatarPrimitive.Fallback
    ref={ref}
    className={cn("flex h-full w-full items-center justify-center rounded-full bg-[#e8e4da] text-sm font-medium", className)}
    {...props}
  />
));
AvatarFallback.displayName = AvatarPrimitive.Fallback.displayName;

export { Avatar, AvatarImage, AvatarFallback };
''')

w("components/ui/tooltip.tsx", '''\
"use client";
import * as React from "react";
import * as TooltipPrimitive from "@radix-ui/react-tooltip";
import { cn } from "@/lib/utils";

const TooltipProvider = TooltipPrimitive.Provider;
const Tooltip = TooltipPrimitive.Root;
const TooltipTrigger = TooltipPrimitive.Trigger;

const TooltipContent = React.forwardRef<
  React.ElementRef<typeof TooltipPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof TooltipPrimitive.Content>
>(({ className, sideOffset = 4, ...props }, ref) => (
  <TooltipPrimitive.Content
    ref={ref}
    sideOffset={sideOffset}
    className={cn(
      "z-50 overflow-hidden rounded-md border border-[#d8d4c8] bg-[#2d2a26] px-3 py-1.5 text-xs text-[#efece4] shadow-md animate-fade-up",
      className
    )}
    {...props}
  />
));
TooltipContent.displayName = TooltipPrimitive.Content.displayName;

export { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider };
''')

# ---------------------------------------------------------------------------
# 2. Supabase clients
# ---------------------------------------------------------------------------

w("lib/supabase/client.ts", '''\
import { createBrowserClient } from "@supabase/ssr";
import type { Database } from "@/types/supabase";

export function createClient() {
  return createBrowserClient<Database>(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
}
''')

w("lib/supabase/server.ts", '''\
import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";
import type { Database } from "@/types/supabase";

export async function createClient() {
  const cookieStore = await cookies();

  return createServerClient<Database>(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll();
        },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options)
            );
          } catch {
            // Server Component — cookie writes ignored
          }
        },
      },
    }
  );
}
''')

w("lib/supabase/middleware.ts", '''\
import { createServerClient } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";

export async function updateSession(request: NextRequest) {
  let supabaseResponse = NextResponse.next({ request });

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value }) =>
            request.cookies.set(name, value)
          );
          supabaseResponse = NextResponse.next({ request });
          cookiesToSet.forEach(({ name, value, options }) =>
            supabaseResponse.cookies.set(name, value, options)
          );
        },
      },
    }
  );

  // Refresh session — do not remove
  const { data: { user } } = await supabase.auth.getUser();

  // Protect dashboard routes
  const isAuthRoute = request.nextUrl.pathname.startsWith("/login") ||
    request.nextUrl.pathname.startsWith("/register");

  if (!user && !isAuthRoute) {
    const url = request.nextUrl.clone();
    url.pathname = "/login";
    return NextResponse.redirect(url);
  }

  return supabaseResponse;
}
''')

# ---------------------------------------------------------------------------
# 3. Root middleware.ts
# ---------------------------------------------------------------------------

w("middleware.ts", '''\
import { type NextRequest } from "next/server";
import { updateSession } from "@/lib/supabase/middleware";

export async function middleware(request: NextRequest) {
  return await updateSession(request);
}

export const config = {
  matcher: [
    /*
     * Match all paths except:
     * - _next/static
     * - _next/image
     * - favicon.ico
     * - public files
     */
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
''')

# ---------------------------------------------------------------------------
# 4. Auth actions (server actions)
# ---------------------------------------------------------------------------

w("app/actions/auth.ts", '''\
"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";

export async function signUp(formData: FormData) {
  const supabase = await createClient();

  const email = formData.get("email") as string;
  const password = formData.get("password") as string;
  const username = formData.get("username") as string;

  const { data, error } = await supabase.auth.signUp({ email, password });

  if (error) {
    return { error: error.message };
  }

  if (data.user) {
    const { error: profileError } = await supabase.from("profiles").insert({
      id: data.user.id,
      username,
      role: "learner",
      xp: 0,
    });

    if (profileError) {
      return { error: profileError.message };
    }
  }

  revalidatePath("/", "layout");
  redirect("/");
}

export async function signIn(formData: FormData) {
  const supabase = await createClient();

  const email = formData.get("email") as string;
  const password = formData.get("password") as string;

  const { error } = await supabase.auth.signInWithPassword({ email, password });

  if (error) {
    return { error: error.message };
  }

  revalidatePath("/", "layout");
  redirect("/");
}

export async function signOut() {
  const supabase = await createClient();
  await supabase.auth.signOut();
  revalidatePath("/", "layout");
  redirect("/login");
}
''')

# ---------------------------------------------------------------------------
# 5. Auth callback route (email confirmation)
# ---------------------------------------------------------------------------

w("app/auth/callback/route.ts", '''\
import { NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";

export async function GET(request: Request) {
  const { searchParams, origin } = new URL(request.url);
  const code = searchParams.get("code");
  const next = searchParams.get("next") ?? "/";

  if (code) {
    const supabase = await createClient();
    const { error } = await supabase.auth.exchangeCodeForSession(code);
    if (!error) {
      return NextResponse.redirect(`${origin}${next}`);
    }
  }

  return NextResponse.redirect(`${origin}/login?error=auth_callback_failed`);
}
''')

# ---------------------------------------------------------------------------
# 6. Login page
# ---------------------------------------------------------------------------

w("app/(auth)/login/page.tsx", '''\
"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const supabase = createClient();
    const { error } = await supabase.auth.signInWithPassword({ email, password });

    if (error) {
      setError(error.message);
      setLoading(false);
      return;
    }

    router.push("/");
    router.refresh();
  }

  return (
    <div className="min-h-screen bg-[#efece4] flex items-center justify-center px-4">
      <div className="w-full max-w-md space-y-6">
        {/* Logo */}
        <div className="text-center space-y-2">
          <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-[#2d2a26]">
            <span className="text-[#efece4] text-lg font-bold">GL</span>
          </div>
          <h1 className="text-2xl font-bold text-[#1a1a1a]">Welcome back</h1>
          <p className="text-sm text-[#6b6560]">Sign in to the Consensus Simulator</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Sign in</CardTitle>
            <CardDescription>Enter your credentials to continue</CardDescription>
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
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
            </CardContent>
            <CardFooter className="flex flex-col gap-3">
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? "Signing in..." : "Sign in"}
              </Button>
              <p className="text-sm text-[#6b6560] text-center">
                Don&apos;t have an account?{" "}
                <Link href="/register" className="text-[#1a1a1a] font-medium hover:underline">
                  Create one
                </Link>
              </p>
            </CardFooter>
          </form>
        </Card>

        <p className="text-center text-xs text-[#6b6560]">
          GenLayer Consensus Simulator · Educational Platform
        </p>
      </div>
    </div>
  );
}
''')

# ---------------------------------------------------------------------------
# 7. Register page
# ---------------------------------------------------------------------------

w("app/(auth)/register/page.tsx", '''\
"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";

export default function RegisterPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

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
    const { data, error: signUpError } = await supabase.auth.signUp({
      email,
      password,
      options: { emailRedirectTo: `${window.location.origin}/auth/callback` },
    });

    if (signUpError) {
      setError(signUpError.message);
      setLoading(false);
      return;
    }

    if (data.user) {
      const { error: profileError } = await supabase.from("profiles").insert({
        id: data.user.id,
        username,
        role: "learner",
        xp: 0,
      });
      if (profileError && !profileError.message.includes("duplicate")) {
        setError(profileError.message);
        setLoading(false);
        return;
      }
    }

    setSuccess(true);
    setLoading(false);

    // If email confirmation is disabled, redirect straight in
    if (data.session) {
      router.push("/");
      router.refresh();
    }
  }

  if (success && !false) {
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
''')

# ---------------------------------------------------------------------------
# 8. Auth layout (no nav wrapper for auth pages)
# ---------------------------------------------------------------------------

w("app/(auth)/layout.tsx", '''\
export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
''')

# ---------------------------------------------------------------------------
# 9. useAuth hook (real implementation)
# ---------------------------------------------------------------------------

w("hooks/useAuth.ts", '''\
"use client";

import { useEffect, useState } from "react";
import type { User } from "@supabase/supabase-js";
import { createClient } from "@/lib/supabase/client";

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const supabase = createClient();

    supabase.auth.getUser().then(({ data }) => {
      setUser(data.user);
      setLoading(false);
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
    });

    return () => subscription.unsubscribe();
  }, []);

  return { user, loading };
}
''')

# ---------------------------------------------------------------------------
# 10. Dashboard layout — with auth user display + sign out
# ---------------------------------------------------------------------------

w("app/(dashboard)/layout.tsx", '''\
import Link from "next/link";
import type { Route } from "next";
import { createClient } from "@/lib/supabase/server";
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
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();

  let username = "Explorer";
  if (user) {
    const { data: profile } = await supabase
      .from("profiles")
      .select("username")
      .eq("id", user.id)
      .single();
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
            {user ? (
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
''')

# ---------------------------------------------------------------------------
# 11. Updated types/supabase.ts — proper Database type shape
# ---------------------------------------------------------------------------

w("types/supabase.ts", '''\
export type Json = string | number | boolean | null | { [key: string]: Json | undefined } | Json[];

export interface Database {
  public: {
    Tables: {
      profiles: {
        Row: {
          id: string;
          username: string;
          role: string;
          xp: number;
          created_at: string;
        };
        Insert: {
          id: string;
          username: string;
          role?: string;
          xp?: number;
          created_at?: string;
        };
        Update: {
          id?: string;
          username?: string;
          role?: string;
          xp?: number;
        };
      };
      claims: {
        Row: {
          id: string;
          user_id: string | null;
          content: string;
          category: string;
          metadata: Json | null;
          created_at: string;
        };
        Insert: {
          id?: string;
          user_id?: string | null;
          content: string;
          category: string;
          metadata?: Json | null;
          created_at?: string;
        };
        Update: {
          content?: string;
          category?: string;
          metadata?: Json | null;
        };
      };
      simulations: {
        Row: {
          id: string;
          claim_id: string;
          user_id: string | null;
          status: string;
          validator_count: number;
          consensus_reached: boolean | null;
          final_verdict: string | null;
          contract_address: string | null;
          tx_hash: string | null;
          chain_data: Json | null;
          created_at: string;
          completed_at: string | null;
        };
        Insert: {
          id?: string;
          claim_id: string;
          user_id?: string | null;
          status?: string;
          validator_count?: number;
          consensus_reached?: boolean | null;
          final_verdict?: string | null;
          contract_address?: string | null;
          tx_hash?: string | null;
          chain_data?: Json | null;
          created_at?: string;
          completed_at?: string | null;
        };
        Update: {
          status?: string;
          consensus_reached?: boolean | null;
          final_verdict?: string | null;
          tx_hash?: string | null;
          chain_data?: Json | null;
          completed_at?: string | null;
        };
      };
      validators: {
        Row: {
          id: string;
          name: string;
          model: string;
          persona: string;
          bias_profile: Json | null;
          is_active: boolean;
          created_at: string;
        };
        Insert: {
          id?: string;
          name: string;
          model: string;
          persona: string;
          bias_profile?: Json | null;
          is_active?: boolean;
          created_at?: string;
        };
        Update: {
          name?: string;
          model?: string;
          persona?: string;
          bias_profile?: Json | null;
          is_active?: boolean;
        };
      };
      validator_votes: {
        Row: {
          id: string;
          simulation_id: string;
          validator_id: string;
          role: string;
          vote: string;
          confidence: number | null;
          reasoning: string | null;
          raw_llm_output: string | null;
          equivalence_score: number | null;
          voted_at: string;
        };
        Insert: {
          id?: string;
          simulation_id: string;
          validator_id: string;
          role?: string;
          vote: string;
          confidence?: number | null;
          reasoning?: string | null;
          raw_llm_output?: string | null;
          equivalence_score?: number | null;
          voted_at?: string;
        };
        Update: {
          vote?: string;
          confidence?: number | null;
          reasoning?: string | null;
          equivalence_score?: number | null;
        };
      };
      consensus_results: {
        Row: {
          id: string;
          simulation_id: string;
          round: number;
          accept_count: number;
          reject_count: number;
          uncertain_count: number;
          consensus_type: string | null;
          equivalence_pass: boolean | null;
          outcome: string | null;
          computed_at: string;
        };
        Insert: {
          id?: string;
          simulation_id: string;
          round?: number;
          accept_count?: number;
          reject_count?: number;
          uncertain_count?: number;
          consensus_type?: string | null;
          equivalence_pass?: boolean | null;
          outcome?: string | null;
          computed_at?: string;
        };
        Update: {
          outcome?: string | null;
          equivalence_pass?: boolean | null;
        };
      };
      appeals: {
        Row: {
          id: string;
          simulation_id: string;
          initiated_by: string | null;
          reason: string;
          status: string;
          additional_validators: number;
          original_outcome: string;
          final_outcome: string | null;
          created_at: string;
          resolved_at: string | null;
        };
        Insert: {
          id?: string;
          simulation_id: string;
          initiated_by?: string | null;
          reason: string;
          status?: string;
          additional_validators?: number;
          original_outcome: string;
          final_outcome?: string | null;
          created_at?: string;
          resolved_at?: string | null;
        };
        Update: {
          status?: string;
          final_outcome?: string | null;
          resolved_at?: string | null;
        };
      };
      appeal_rounds: {
        Row: {
          id: string;
          appeal_id: string;
          round: number;
          outcome: string | null;
          votes_data: Json | null;
          created_at: string;
        };
        Insert: {
          id?: string;
          appeal_id: string;
          round: number;
          outcome?: string | null;
          votes_data?: Json | null;
          created_at?: string;
        };
        Update: {
          outcome?: string | null;
          votes_data?: Json | null;
        };
      };
      analytics_events: {
        Row: {
          id: string;
          user_id: string | null;
          event_type: string;
          payload: Json | null;
          created_at: string;
        };
        Insert: {
          id?: string;
          user_id?: string | null;
          event_type: string;
          payload?: Json | null;
          created_at?: string;
        };
        Update: never;
      };
      audit_logs: {
        Row: {
          id: string;
          user_id: string | null;
          action: string;
          table_name: string | null;
          record_id: string | null;
          diff: Json | null;
          ip_address: string | null;
          created_at: string;
        };
        Insert: {
          id?: string;
          user_id?: string | null;
          action: string;
          table_name?: string | null;
          record_id?: string | null;
          diff?: Json | null;
          ip_address?: string | null;
          created_at?: string;
        };
        Update: never;
      };
    };
    Views: Record<string, never>;
    Functions: Record<string, never>;
    Enums: Record<string, never>;
  };
}
''')

# ---------------------------------------------------------------------------
# 12. .env.local template (gitignored, needs user values)
# ---------------------------------------------------------------------------

env_local = ROOT / ".env.local"
if not env_local.exists():
    w(".env.local", """\
# ─── Supabase ────────────────────────────────────────────────────────────────
# Get these from: https://supabase.com/dashboard → your project → Settings → API
NEXT_PUBLIC_SUPABASE_URL=https://YOUR_PROJECT_ID.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=YOUR_ANON_KEY
SUPABASE_SERVICE_ROLE_KEY=YOUR_SERVICE_ROLE_KEY

# ─── GenLayer ────────────────────────────────────────────────────────────────
NEXT_PUBLIC_GENLAYER_RPC_URL=
NEXT_PUBLIC_CONTRACT_ADDRESS_CONSENSUS=
NEXT_PUBLIC_CONTRACT_ADDRESS_APPEALS=
NEXT_PUBLIC_GENLAYER_CHAIN_ID=

# ─── App ─────────────────────────────────────────────────────────────────────
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXTAUTH_SECRET=

# ─── Monitoring ──────────────────────────────────────────────────────────────
SENTRY_DSN=
""")
    print("  WROTE  .env.local (template — fill in Supabase values)")
else:
    print("  SKIP   .env.local (already exists — not overwriting)")

# ---------------------------------------------------------------------------
# 13. .gitignore — make sure .env.local is excluded
# ---------------------------------------------------------------------------

w(".gitignore", """\
# Dependencies
node_modules/
.pnp
.pnp.js

# Next.js
.next/
out/

# Environment files
.env.local
.env.*.local

# Vercel
.vercel

# TypeScript
*.tsbuildinfo
next-env.d.ts

# OS
.DS_Store
Thumbs.db

# Logs
*.log
npm-debug.log*
""")

print(f"\nPhase 3 complete. All files written.\n")
