"""Push FIREBASE_SERVICE_ACCOUNT_KEY to Vercel as a single-line JSON string.

Usage: set FIREBASE_SERVICE_ACCOUNT_KEY=<json> and run this script,
       or paste the service account JSON inline before running.
"""
import subprocess, pathlib, json, os

ROOT = pathlib.Path("C:/GenB/GenLayer Consensus Simulator")

# Load from environment or paste JSON here (do not commit credentials)
raw = os.environ.get("FIREBASE_SERVICE_ACCOUNT_KEY", "")
if not raw:
    raise SystemExit("Set FIREBASE_SERVICE_ACCOUNT_KEY env var before running.")

value = json.dumps(json.loads(raw))  # normalise to single line

for env in ("production", "preview", "development"):
    r = subprocess.run(
        ["vercel", "env", "add", "FIREBASE_SERVICE_ACCOUNT_KEY", env, "--force"],
        input=value.encode("utf-8"),
        capture_output=True, cwd=ROOT, shell=True,
    )
    status = "OK" if r.returncode == 0 else "FAIL"
    print(f"  {status}  FIREBASE_SERVICE_ACCOUNT_KEY -> {env}")

print("\nDone.")
