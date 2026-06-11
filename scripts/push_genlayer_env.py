"""Push GenLayer Studio Net env vars to Vercel."""
import subprocess, pathlib

ROOT = pathlib.Path("C:/GenB/GenLayer Consensus Simulator")

VARS = {
    "NEXT_PUBLIC_GENLAYER_PRIVATE_KEY": "0x78c31f4f26d022683cf6edfae1e368a246d9cf5ecca32ab6729f6dfa9c68409f",
    "NEXT_PUBLIC_GENLAYER_RPC_URL":     "http://localhost:4000/api",
}

ENVS = ["production", "preview", "development"]

for name, value in VARS.items():
    for env in ENVS:
        r = subprocess.run(
            ["vercel", "env", "add", name, env, "--force"],
            input=value.encode("utf-8"),
            capture_output=True, cwd=ROOT, shell=True,
        )
        status = "OK" if r.returncode == 0 else "??"
        print(f"  {status}  {name} -> {env}")

print("\nAll GenLayer env vars pushed.")
