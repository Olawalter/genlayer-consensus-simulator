import { cookies } from "next/headers";
import { adminAuth } from "./admin";

export const SESSION_COOKIE = "fb_session";
export const SESSION_MAX_AGE = 60 * 60 * 24 * 14;

export async function createSessionCookie(idToken: string): Promise<string> {
  const expiresIn = SESSION_MAX_AGE * 1000;
  return adminAuth.createSessionCookie(idToken, { expiresIn });
}

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

export async function getServerUser(): Promise<{ uid: string; email?: string } | null> {
  const cookieStore = await cookies();
  const session = cookieStore.get(SESSION_COOKIE)?.value;
  if (!session) return null;
  return verifySessionCookie(session);
}
