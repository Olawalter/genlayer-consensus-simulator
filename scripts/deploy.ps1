# GenLayer Consensus Simulator — Local Deploy Helper
# Usage: .\scripts\deploy.ps1 [-Preview] [-Prod]
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
