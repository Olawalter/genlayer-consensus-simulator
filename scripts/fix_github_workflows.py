"""Fix GitHub Actions workflows."""
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
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"

      - name: Install dependencies
        run: npm ci

      - name: Build
        run: npm run build
        env:
          NEXT_PUBLIC_FIREBASE_API_KEY: placeholder
          NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN: placeholder.firebaseapp.com
          NEXT_PUBLIC_FIREBASE_PROJECT_ID: placeholder
          NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET: placeholder.appspot.com
          NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID: "000000000000"
          NEXT_PUBLIC_FIREBASE_APP_ID: "1:000000000000:web:placeholder"
          FIREBASE_SERVICE_ACCOUNT_KEY: ${{ secrets.FIREBASE_SERVICE_ACCOUNT_KEY }}
          NEXT_PUBLIC_GENLAYER_PRIVATE_KEY: "0x0000000000000000000000000000000000000000000000000000000000000001"
          NEXT_PUBLIC_GENLAYER_RPC_URL: http://localhost:4000/api
          NEXT_PUBLIC_APP_URL: https://genlayer-consensus-simulator.vercel.app
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

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"

      - name: Install dependencies
        run: npm ci

      - name: Deploy to Vercel
        run: npx vercel --prod --yes --token=${{ secrets.VERCEL_TOKEN }}
        env:
          VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
          VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}
''', encoding="utf-8")
print(f"Written: {deploy}")
