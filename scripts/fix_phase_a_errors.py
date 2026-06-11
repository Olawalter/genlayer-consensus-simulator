"""Fix two build errors from Phase A."""
import pathlib

ROOT = pathlib.Path("C:/GenB/GenLayer Consensus Simulator")

# 1. Fix chains import — studionet is a named export, not under 'chains'
p = ROOT / "lib/genlayer/client.ts"
content = p.read_text(encoding="utf-8")
content = content.replace(
    'import { chains } from "genlayer-js/chains";',
    'import { studionet } from "genlayer-js/chains";'
).replace(
    'chain: chains.studionet,',
    'chain: studionet,'
)
p.write_bytes(content.encode("utf-8"))
print("fixed lib/genlayer/client.ts — chains import")

# 2. Fix setCurrentResult(null) type error — store likely expects SandboxExecutionResult | null
# Check what the store type is
store_path = ROOT / "store/sandboxStore.ts"
store_content = store_path.read_text(encoding="utf-8")
print("sandboxStore setCurrentResult signature:")
for line in store_content.splitlines():
    if "setCurrentResult" in line or "currentResult" in line:
        print(" ", line)

# Fix by casting null as any in the page, or updating the store to accept null
# Easier: update store to accept null
if "SandboxExecutionResult | null" not in store_content and "currentResult:" in store_content:
    # Store likely has currentResult: SandboxExecutionResult — make it nullable
    store_content = store_content.replace(
        "currentResult: SandboxExecutionResult;",
        "currentResult: SandboxExecutionResult | null;"
    ).replace(
        "setCurrentResult: (r: SandboxExecutionResult) => void;",
        "setCurrentResult: (r: SandboxExecutionResult | null) => void;"
    )
    store_path.write_bytes(store_content.encode("utf-8"))
    print("fixed store/sandboxStore.ts — currentResult nullable")
else:
    # Already nullable or different shape — patch the page instead
    page = ROOT / "app/(dashboard)/sandbox/page.tsx"
    page_content = page.read_text(encoding="utf-8")
    page_content = page_content.replace(
        "setCurrentResult(null);",
        "setCurrentResult(null as unknown as import('@/lib/sandbox/executor').SandboxExecutionResult);"
    )
    page.write_bytes(page_content.encode("utf-8"))
    print("fixed sandbox/page.tsx — setCurrentResult null cast")
