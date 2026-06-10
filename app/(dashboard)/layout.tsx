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
      .single<{ username: string }>();
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
