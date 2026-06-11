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

  signIn:         (email: string, password: string) => Promise<string | null>;
  signUp:         (email: string, password: string, username: string) => Promise<string | null>;
  signOut:        () => Promise<void>;
  refreshProfile: () => Promise<void>;
  init:           () => () => void;
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
