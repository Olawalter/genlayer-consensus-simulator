import { type NextRequest, NextResponse } from "next/server";
import { SESSION_COOKIE } from "@/lib/firebase/auth-helpers";

export const runtime = "nodejs";

const PUBLIC_PATHS = ["/login", "/register", "/api/auth/session"];

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

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

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|.*\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
