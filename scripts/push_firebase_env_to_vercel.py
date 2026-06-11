"""Push Firebase env vars to Vercel — no UTF-8 BOM (uses subprocess bytes input)."""
import subprocess, sys, pathlib

ROOT = pathlib.Path("C:/GenB/GenLayer Consensus Simulator")

VARS = {
    "NEXT_PUBLIC_FIREBASE_API_KEY":             "AIzaSyDS_chVpGjQ68gWKl9mbFdkonftFlS61vo",
    "NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN":         "genlayer-consensus-simulator.firebaseapp.com",
    "NEXT_PUBLIC_FIREBASE_DATABASE_URL":        "https://genlayer-consensus-simulator-default-rtdb.firebaseio.com",
    "NEXT_PUBLIC_FIREBASE_PROJECT_ID":          "genlayer-consensus-simulator",
    "NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET":      "genlayer-consensus-simulator.firebasestorage.app",
    "NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID": "342879568776",
    "NEXT_PUBLIC_FIREBASE_APP_ID":              "1:342879568776:web:17641a97558b57a39e703d",
    "NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID":      "G-QDP7C3ECLW",
    "NEXT_PUBLIC_APP_URL":                      "https://genlayer-consensus-simulator.vercel.app",
    "NEXTAUTH_SECRET":                          "WWFHbAXsnOGAPgu6k3W7Ig3AsdDSfgnfBCqxvC/mSmk=",
}

# FIREBASE_SERVICE_ACCOUNT_KEY must be set separately once the user provides the JSON
# Run: python scripts/set_service_account.py  after getting the key from Firebase console

ENVS = ["production", "preview", "development"]

def push(name: str, value: str) -> None:
    assert value.isascii(), f"Non-ASCII in {name}"
    for env in ENVS:
        result = subprocess.run(
            ["vercel", "env", "add", name, env, "--force"],
            input=value.encode("ascii"),
            capture_output=True,
            cwd=ROOT,
            shell=True,
        )
        out = (result.stdout + result.stderr).decode("utf-8", errors="replace")
        status = "OK" if result.returncode == 0 else "??"
        print(f"  {status}  {name} -> {env}")

print("Pushing Firebase env vars to Vercel...\n")
for name, value in VARS.items():
    push(name, value)

print("\nDone. Now removing old Supabase vars (if any)...")
for old_var in ["NEXT_PUBLIC_SUPABASE_URL", "NEXT_PUBLIC_SUPABASE_ANON_KEY", "SUPABASE_SERVICE_ROLE_KEY"]:
    for env in ENVS:
        subprocess.run(
            ["vercel", "env", "rm", old_var, env, "--yes"],
            cwd=ROOT, shell=True, capture_output=True
        )
    print(f"  removed  {old_var}")

print("\nDeploying to production...")
deploy = subprocess.run(
    ["vercel", "--prod", "--yes"],
    cwd=ROOT, shell=True,
    capture_output=True, text=True,
)
lines = (deploy.stdout + deploy.stderr).strip().split("\n")
for line in lines[-30:]:
    print(line)

if deploy.returncode != 0:
    print("\nDeploy failed — check output above.")
    sys.exit(1)
print("\nDeployed!")
