import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json() as { claim?: string; category?: string };
    const { claim, category } = body;

    if (!claim || typeof claim !== "string" || claim.trim().length < 10) {
      return NextResponse.json({ error: "Claim must be at least 10 characters." }, { status: 400 });
    }

    if (!["freelance", "review", "event", "custom"].includes(category ?? "")) {
      return NextResponse.json({ error: "Invalid category." }, { status: 400 });
    }

    // Simulation runs client-side for now; this route will persist results to Supabase
    // when the DB connection is live (Phase 5 integration).
    return NextResponse.json({
      status: "ok",
      message: "Simulation accepted. Running client-side with live Supabase persistence in Phase 5.",
    });
  } catch {
    return NextResponse.json({ error: "Invalid request body." }, { status: 400 });
  }
}
