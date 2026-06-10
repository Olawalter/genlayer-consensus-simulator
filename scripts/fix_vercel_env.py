"""Re-add all Vercel env vars cleanly — no UTF-8 BOM.
PowerShell echo pipes add a BOM (U+FEFF) which breaks HTTP headers.
Python subprocess with input=bytes avoids this entirely.
"""
import subprocess, sys, pathlib

ROOT = pathlib.Path("C:/GenB/GenLayer Consensus Simulator")

VARS = {
    "NEXT_PUBLIC_SUPABASE_URL":
        "https://osjbxbykfcgeizohkker.supabase.co",
    "NEXT_PUBLIC_SUPABASE_ANON_KEY":
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        ".eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9zamJ4YnlrZmNnZWl6b2hra2VyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODExMjU0ODgsImV4cCI6MjA5NjcwMTQ4OH0"
        ".46WbFG2nfgX2d6UTUfHalH-ULN_9zIeE25BhQKYJo1A",
    "SUPABASE_SERVICE_ROLE_KEY":
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        ".eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9zamJ4YnlrZmNnZWl6b2hra2VyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTEyNTQ4OCwiZXhwIjoyMDk2NzAxNDg4fQ"
        ".3jb9mBYQyIaVaC7qibGfFFa1tOOIInaNa8CIzRs-5lo",
    "NEXT_PUBLIC_APP_URL":
        "https://genlayer-consensus-simulator.vercel.app",
    "NEXTAUTH_SECRET":
        "WWFHbAXsnOGAPgu6k3W7Ig3AsdDSfgnfBCqxvC/mSmk=",
}

ENVS = ["production", "development"]

def run_vercel(args: list[str], value: str) -> bool:
    """Run vercel CLI piping value as clean ASCII bytes — zero BOM."""
    result = subprocess.run(
        ["vercel"] + args,
        input=value.encode("ascii"),   # pure ASCII, no BOM
        capture_output=True,
        cwd=ROOT,
        shell=True,
    )
    out = result.stdout.decode("utf-8", errors="replace")
    err = result.stderr.decode("utf-8", errors="replace")
    if "Overrode" in out or "Added" in out or "Saving" in out:
        return True
    if result.returncode != 0:
        print(f"    WARN: {(err or out).strip()[:120]}")
    return result.returncode == 0

print("Re-adding all Vercel env vars without BOM...\n")

for name, value in VARS.items():
    # Verify no non-ASCII slipped in
    assert value.isascii(), f"Non-ASCII in {name}!"
    for env in ENVS:
        ok = run_vercel(["env", "add", name, env, "--force"], value)
        status = "OK" if ok else "??"
        print(f"  {status}  {name} -> {env}")

print("\nAll env vars re-added cleanly.")
print("Now triggering production redeploy...\n")

deploy = subprocess.run(
    ["vercel", "--prod", "--yes"],
    cwd=ROOT, shell=True,
    capture_output=True, text=True,
)
# Print last 30 lines of output
lines = (deploy.stdout + deploy.stderr).strip().split("\n")
for line in lines[-30:]:
    print(line)

if deploy.returncode == 0:
    print("\nRedeploy successful — BOM-free env vars now baked into build.")
else:
    print("\nDeploy failed — check output above.")
    sys.exit(1)
