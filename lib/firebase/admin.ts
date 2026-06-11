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
