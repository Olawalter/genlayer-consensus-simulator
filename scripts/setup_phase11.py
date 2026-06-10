"""Phase 11 — Vercel Deployment + CI/CD Pipeline
Creates: .gitignore, vercel.json, .env.example,
         .github/workflows/ci.yml, .github/workflows/deploy.yml,
         scripts/deploy.ps1
Then initializes git repo, makes initial commit, installs Vercel CLI,
and runs vercel deploy.
"""
import pathlib, subprocess, sys, os

ROOT = pathlib.Path("C:/GenB/GenLayer Consensus Simulator")

def write(rel: str, code: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(code.encode("utf-8"))
    print(f"  wrote  {rel}")

def run(*args, check=True, capture=False, **kwargs):
    return subprocess.run(
        list(args), cwd=ROOT, check=check,
        capture_output=capture, text=True, shell=True, **kwargs
    )

# ─────────────────────────────────────────────────────────────────────────────
# 1. .gitignore
# ─────────────────────────────────────────────────────────────────────────────
write(".gitignore", """\
# Dependencies
node_modules/
.pnp
.pnp.js

# Next.js build output
.next/
out/
build/
dist/

# Environment variables — NEVER commit these
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Vercel
.vercel/

# Debug logs
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*

# OS
.DS_Store
Thumbs.db
desktop.ini

# Editor
.vscode/
.idea/
*.swp
*.swo
*~

# TypeScript
*.tsbuildinfo
next-env.d.ts

# Testing
coverage/
.nyc_output/

# Python scripts (build tooling only — not part of the app)
__pycache__/
*.pyc
*.pyo
scripts/__pycache__/
""")

# ─────────────────────────────────────────────────────────────────────────────
# 2. vercel.json
# ─────────────────────────────────────────────────────────────────────────────
write("vercel.json", """\
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "outputDirectory": ".next",
  "regions": ["iad1"],
  "env": {
    "NEXT_PUBLIC_APP_URL": "@app_url"
  },
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options",    "value": "nosniff" },
        { "key": "X-Frame-Options",            "value": "DENY" },
        { "key": "X-XSS-Protection",           "value": "1; mode=block" },
        { "key": "Referrer-Policy",            "value": "strict-origin-when-cross-origin" },
        {
          "key": "Permissions-Policy",
          "value": "camera=(), microphone=(), geolocation=()"
        }
      ]
    }
  ]
}
""")

# ─────────────────────────────────────────────────────────────────────────────
# 3. .env.example  (safe to commit — no real secrets)
# ─────────────────────────────────────────────────────────────────────────────
write(".env.example", """\
# ── Supabase ──────────────────────────────────────────────────────────────────
# Get these from: https://supabase.com/dashboard → your project → Settings → API
NEXT_PUBLIC_SUPABASE_URL=https://YOUR_PROJECT_ID.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=YOUR_ANON_KEY
SUPABASE_SERVICE_ROLE_KEY=YOUR_SERVICE_ROLE_KEY

# ── GenLayer ──────────────────────────────────────────────────────────────────
# Asimov Testnet RPC endpoint (https://docs.genlayer.com)
NEXT_PUBLIC_GENLAYER_RPC_URL=https://studio.genlayer.com:8443/api
NEXT_PUBLIC_CONTRACT_ADDRESS_CONSENSUS=
NEXT_PUBLIC_CONTRACT_ADDRESS_APPEALS=
NEXT_PUBLIC_GENLAYER_CHAIN_ID=

# ── App ───────────────────────────────────────────────────────────────────────
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXTAUTH_SECRET=generate-with-openssl-rand-base64-32

# ── Monitoring (optional) ─────────────────────────────────────────────────────
SENTRY_DSN=
""")

# ─────────────────────────────────────────────────────────────────────────────
# 4. .github/workflows/ci.yml
# ─────────────────────────────────────────────────────────────────────────────
write(".github/workflows/ci.yml", """\
name: CI

on:
  push:
    branches: ["**"]
  pull_request:
    branches: [main]

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  build:
    name: Type-check & Build
    runs-on: ubuntu-latest
    timeout-minutes: 15

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node.js 20
        uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"

      - name: Install dependencies
        run: npm ci

      - name: Build (includes type-check)
        run: npm run build
        env:
          NEXT_PUBLIC_SUPABASE_URL: ${{ secrets.NEXT_PUBLIC_SUPABASE_URL || 'https://placeholder.supabase.co' }}
          NEXT_PUBLIC_SUPABASE_ANON_KEY: ${{ secrets.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'placeholder_anon_key' }}
          NEXT_PUBLIC_APP_URL: https://genlayer-consensus-simulator.vercel.app

      - name: Upload build artifacts
        if: github.ref == 'refs/heads/main'
        uses: actions/upload-artifact@v4
        with:
          name: nextjs-build
          path: .next/
          retention-days: 1
""")

# ─────────────────────────────────────────────────────────────────────────────
# 5. .github/workflows/deploy.yml
# ─────────────────────────────────────────────────────────────────────────────
write(".github/workflows/deploy.yml", """\
name: Deploy to Vercel

on:
  push:
    branches: [main]

concurrency:
  group: deploy-production
  cancel-in-progress: false

jobs:
  deploy:
    name: Deploy Production
    runs-on: ubuntu-latest
    timeout-minutes: 20
    environment:
      name: production
      url: ${{ steps.deploy.outputs.url }}

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node.js 20
        uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"

      - name: Install dependencies
        run: npm ci

      - name: Deploy to Vercel
        id: deploy
        run: |
          URL=$(npx vercel --prod --yes --token=${{ secrets.VERCEL_TOKEN }})
          echo "url=$URL" >> $GITHUB_OUTPUT
          echo "Deployed to: $URL"
        env:
          VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
          VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}

      - name: Comment deployment URL on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '🚀 Deployed to: ${{ steps.deploy.outputs.url }}'
            })
""")

# ─────────────────────────────────────────────────────────────────────────────
# 6. scripts/deploy.ps1 — one-click local deploy helper
# ─────────────────────────────────────────────────────────────────────────────
write("scripts/deploy.ps1", """\
# GenLayer Consensus Simulator — Local Deploy Helper
# Usage: .\\scripts\\deploy.ps1 [-Preview] [-Prod]
param(
  [switch]$Preview,
  [switch]$Prod
)

$root = Split-Path $PSScriptRoot -Parent
Set-Location $root

Write-Host "`n  GenLayer Consensus Simulator — Deploy" -ForegroundColor Cyan
Write-Host "  ─────────────────────────────────────" -ForegroundColor DarkGray

# 1. Build check
Write-Host "`n[1/3] Running production build..." -ForegroundColor Yellow
npm run build
if ($LASTEXITCODE -ne 0) {
  Write-Host "Build failed. Fix errors before deploying." -ForegroundColor Red
  exit 1
}

# 2. Vercel CLI check
$vercelPath = Get-Command vercel -ErrorAction SilentlyContinue
if (-not $vercelPath) {
  Write-Host "`n[2/3] Installing Vercel CLI globally..." -ForegroundColor Yellow
  npm install -g vercel
} else {
  Write-Host "`n[2/3] Vercel CLI found: $($vercelPath.Source)" -ForegroundColor Green
}

# 3. Deploy
Write-Host "`n[3/3] Deploying..." -ForegroundColor Yellow
if ($Prod) {
  Write-Host "  Mode: PRODUCTION" -ForegroundColor Magenta
  vercel --prod --yes
} else {
  Write-Host "  Mode: PREVIEW (pass -Prod for production)" -ForegroundColor Cyan
  vercel --yes
}

if ($LASTEXITCODE -eq 0) {
  Write-Host "`n  Deployment complete." -ForegroundColor Green
} else {
  Write-Host "`n  Deployment failed." -ForegroundColor Red
  exit 1
}
""")

# ─────────────────────────────────────────────────────────────────────────────
# 7. Initialize git repository
# ─────────────────────────────────────────────────────────────────────────────
print("\n[git] Initializing repository...")
run("git", "init", "-b", "main")
run("git", "config", "user.email", "dev@genlayer-simulator.local")
run("git", "config", "user.name", "GenLayer Simulator")

# Stage all files (respects .gitignore)
print("[git] Staging files...")
run("git", "add", ".")

# Check what's staged
result = run("git", "status", "--short", capture=True, check=False)
print(result.stdout[:2000] if result.stdout else "(nothing staged)")

print("[git] Creating initial commit...")
commit_msg = """\
Initial commit: GenLayer Consensus Simulator

Full-stack Next.js 15 educational platform for learning GenLayer,
Intelligent Contracts, Optimistic Democracy, Equivalence Principle,
Appeals, Validator Nodes, LLM Comparison, and developer tooling.

Modules:
- Consensus Playground (/playground)
- Validator Lab (/validator-lab)
- Appeals Arena (/appeals)
- Equivalence Explorer (/equivalence)
- Optimistic Democracy Dashboard (/democracy)
- LLM Comparison Center (/llm-compare)
- Learning Center (/learn)
- Developer Sandbox (/sandbox)

Stack: Next.js 15.5 + TypeScript + Tailwind CSS 3.4 + Supabase +
Zustand v5 + Framer Motion v12 + shadcn/ui + Radix Primitives"""

run("git", "commit", "-m", commit_msg)

# Show commit summary
result = run("git", "log", "--oneline", "-1", capture=True, check=False)
print(f"[git] Committed: {result.stdout.strip()}")

result = run("git", "diff", "--stat", "HEAD~1", "HEAD", capture=True, check=False)
if result.returncode != 0:
    # First commit — use diff-tree
    result = run("git", "diff-tree", "--stat", "--no-commit-id", "-r", "HEAD", capture=True, check=False)
print(result.stdout[:1500] if result.stdout else "")

# ─────────────────────────────────────────────────────────────────────────────
# 8. Install Vercel CLI + link project
# ─────────────────────────────────────────────────────────────────────────────
print("\n[vercel] Checking Vercel CLI...")
vc = run("vercel", "--version", capture=True, check=False)
if vc.returncode != 0:
    print("[vercel] Installing Vercel CLI globally...")
    run("npm", "install", "-g", "vercel")
    vc = run("vercel", "--version", capture=True, check=False)

print(f"[vercel] CLI version: {vc.stdout.strip()}")

print("\n[vercel] Pulling project settings (login required if first time)...")
link = run("vercel", "pull", "--yes", capture=True, check=False)
if link.returncode != 0:
    print("[vercel] Not linked yet — running 'vercel' to authenticate and link project...")
    print("         Follow the prompts in your browser.\n")
    # Interactive link — must not capture output
    result = subprocess.run(["vercel", "--yes"], cwd=ROOT, shell=True)
    if result.returncode != 0:
        print("\n[vercel] Linking failed or was cancelled.")
        print("         Run: vercel   (in the project directory) to retry.")
        print("         Then run: vercel --prod   to deploy to production.")
        sys.exit(0)  # Not a fatal error — project is fully built
else:
    print(link.stdout.strip())
    # Deploy preview
    print("\n[vercel] Deploying preview build...")
    deploy = subprocess.run(["vercel", "--yes"], cwd=ROOT, shell=True)

print("\n[Phase 11] All files written and git repo initialized.")
print("  To deploy production:  vercel --prod")
print("  To push to GitHub:     git remote add origin <URL> && git push -u origin main")
