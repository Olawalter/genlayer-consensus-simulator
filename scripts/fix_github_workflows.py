"""Fix GitHub Actions workflows: update CI to use Firebase env vars, fix deploy workflow."""
import pathlib

ROOT = pathlib.Path("C:/GenB/GenLayer Consensus Simulator")

# ── ci.yml ────────────────────────────────────────────────────────────────────
ci = ROOT / ".github/workflows/ci.yml"
ci.write_text('''\
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
          NEXT_PUBLIC_FIREBASE_API_KEY: placeholder
          NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN: placeholder.firebaseapp.com
          NEXT_PUBLIC_FIREBASE_PROJECT_ID: placeholder
          NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET: placeholder.appspot.com
          NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID: "000000000000"
          NEXT_PUBLIC_FIREBASE_APP_ID: placeholder
          FIREBASE_SERVICE_ACCOUNT_KEY: \'{"type":"service_account","project_id":"placeholder","private_key_id":"placeholder","private_key":"-----BEGIN PRIVATE KEY-----\\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQC7placeholder\\n-----END PRIVATE KEY-----\\n","client_email":"placeholder@placeholder.iam.gserviceaccount.com","client_id":"000000000000000000000","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"https://www.googleapis.com/robot/v1/metadata/x509/placeholder"}\'
          NEXT_PUBLIC_GENLAYER_PRIVATE_KEY: "0x0000000000000000000000000000000000000000000000000000000000000001"
          NEXT_PUBLIC_GENLAYER_RPC_URL: http://localhost:4000/api
          NEXT_PUBLIC_APP_URL: https://genlayer-consensus-simulator.vercel.app

      - name: Upload build artifacts
        if: github.ref == \'refs/heads/main\'
        uses: actions/upload-artifact@v4
        with:
          name: nextjs-build
          path: .next/
          retention-days: 1
''', encoding="utf-8")
print(f"Written: {ci}")

# ── deploy.yml ────────────────────────────────────────────────────────────────
deploy = ROOT / ".github/workflows/deploy.yml"
deploy.write_text('''\
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
          OUTPUT=$(npx vercel --prod --yes --token=${{ secrets.VERCEL_TOKEN }})
          URL=$(echo "$OUTPUT" | grep -o \'https://[^ ]*\' | tail -1)
          echo "url=$URL" >> $GITHUB_OUTPUT
          echo "Deployed to: $URL"
        env:
          VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
          VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}
''', encoding="utf-8")
print(f"Written: {deploy}")
print("Done. Now set these GitHub secrets:")
print("  VERCEL_TOKEN   — from vercel.com/account/tokens")
print("  VERCEL_ORG_ID  — team_Xy1P2lfaLskK75VcqGddyq9s")
print("  VERCEL_PROJECT_ID — prj_dmEGUHgpWXeccz2R29i5zq3AFSG4")
