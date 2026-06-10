import Link from "next/link";
import type { Route } from "next";

type Module = {
  href: Route;
  title: string;
  description: string;
  icon: string;
  color: string;
};

const modules: Module[] = [
  {
    href: "/playground",
    title: "Consensus Playground",
    description: "Submit subjective claims and watch validators reach consensus in real time.",
    icon: "⚡",
    color: "border-indigo-200 hover:border-indigo-400",
  },
  {
    href: "/validator-lab",
    title: "Validator Lab",
    description: "Experiment with validator personalities, models, and bias profiles.",
    icon: "🧪",
    color: "border-emerald-200 hover:border-emerald-400",
  },
  {
    href: "/appeals",
    title: "Appeals Arena",
    description: "Challenge disputed decisions and observe how new consensus forms.",
    icon: "⚖️",
    color: "border-purple-200 hover:border-purple-400",
  },
  {
    href: "/equivalence",
    title: "Equivalence Explorer",
    description: "Visualize the acceptable disagreement ranges between validators.",
    icon: "🔭",
    color: "border-cyan-200 hover:border-cyan-400",
  },
  {
    href: "/democracy",
    title: "Optimistic Democracy",
    description: "See exactly how Optimistic Democracy forms consensus on-chain.",
    icon: "🗳️",
    color: "border-amber-200 hover:border-amber-400",
  },
  {
    href: "/llm-compare",
    title: "LLM Comparison Center",
    description: "Compare outputs from different GenLayer-enabled AI models side by side.",
    icon: "🤖",
    color: "border-pink-200 hover:border-pink-400",
  },
  {
    href: "/learn",
    title: "Learning Center",
    description: "Interactive explanations of every GenLayer concept.",
    icon: "📚",
    color: "border-orange-200 hover:border-orange-400",
  },
  {
    href: "/sandbox",
    title: "Developer Sandbox",
    description: "Test consensus scenarios and explore the SDK hands-on.",
    icon: "🛠️",
    color: "border-slate-200 hover:border-slate-400",
  },
];

export default function DashboardPage() {
  return (
    <main className="min-h-screen bg-[#efece4]">
      {/* Hero */}
      <div className="px-6 pt-16 pb-12 text-center max-w-4xl mx-auto">
        <div className="inline-flex items-center gap-2 rounded-full border border-[#d8d4c8] bg-white/50 px-4 py-1.5 text-sm text-[#6b6560] mb-6">
          <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
          GenLayer Studio Net
        </div>
        <h1 className="text-5xl font-bold tracking-tight text-[#1a1a1a] mb-4">
          GenLayer Consensus Simulator
        </h1>
        <p className="text-xl text-[#6b6560] max-w-2xl mx-auto leading-relaxed">
          An interactive educational platform for understanding Intelligent Contracts,
          Optimistic Democracy, and Subjective Consensus on GenLayer.
        </p>
      </div>

      {/* Module Grid */}
      <div className="px-6 pb-16 max-w-6xl mx-auto">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {modules.map((mod) => (
            <Link key={mod.href} href={mod.href}>
              <div
                className={`h-full rounded-xl border-2 bg-white/60 backdrop-blur-sm p-6 transition-all duration-200 hover:bg-white/80 hover:shadow-md cursor-pointer ${mod.color}`}
              >
                <div className="text-3xl mb-3">{mod.icon}</div>
                <h2 className="font-semibold text-[#1a1a1a] mb-2 text-sm">
                  {mod.title}
                </h2>
                <p className="text-xs text-[#6b6560] leading-relaxed">
                  {mod.description}
                </p>
              </div>
            </Link>
          ))}
        </div>

        {/* Concept callouts */}
        <div className="mt-10 grid grid-cols-1 sm:grid-cols-3 gap-4">
          {[
            { label: "Equivalence Principle", desc: "Validators accept outputs within a defined margin of similarity — not exact matches." },
            { label: "Optimistic Democracy", desc: "Leader proposes → validators confirm → finality window → on-chain settlement." },
            { label: "Appeals Process", desc: "Any party can challenge a verdict, triggering an expanded validator round." },
          ].map((c) => (
            <div key={c.label} className="rounded-xl border border-[#d8d4c8] bg-white/40 p-5">
              <p className="text-xs font-semibold text-[#2d2a26] uppercase tracking-wider mb-2">
                {c.label}
              </p>
              <p className="text-sm text-[#6b6560] leading-relaxed">{c.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
