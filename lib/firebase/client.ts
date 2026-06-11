import { initializeApp, getApps, getApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

const firebaseConfig = {
  apiKey:            "AIzaSyDS_chVpGjQ68gWKl9mbFdkonftFlS61vo",
  authDomain:        "genlayer-consensus-simulator.firebaseapp.com",
  databaseURL:       "https://genlayer-consensus-simulator-default-rtdb.firebaseio.com",
  projectId:         "genlayer-consensus-simulator",
  storageBucket:     "genlayer-consensus-simulator.firebasestorage.app",
  messagingSenderId: "342879568776",
  appId:             "1:342879568776:web:17641a97558b57a39e703d",
  measurementId:     "G-QDP7C3ECLW",
};

const app = getApps().length ? getApp() : initializeApp(firebaseConfig);

export const auth = getAuth(app);
export const db   = getFirestore(app);
export default app;
