import {
  doc, getDoc, setDoc, updateDoc,
  collection, query, where, getDocs, addDoc,
  serverTimestamp, type DocumentData,
} from "firebase/firestore";
import { db } from "./client";

export interface UserProfile {
  uid:       string;
  username:  string;
  email:     string;
  role:      "learner" | "admin";
  xp:        number;
  createdAt: unknown;
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
