# BEM 100 v2.0 — Indian Stock Momentum & Breakout Intelligence Platform

[![Daily Post-Market Screener](https://github.com/AshayKatkar/StockMarket_WatchKeeper/actions/workflows/daily_bem_update.yml/badge.svg)](https://github.com/AshayKatkar/StockMarket_WatchKeeper/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg?logo=next.js)](https://nextjs.org)
[![PWA Ready](https://img.shields.io/badge/PWA-Installed-10b981.svg)](https://web.dev/progressive-web-apps/)

Production-grade quantitative Indian equity momentum and breakout screening platform engineered with a strict **Zero-Cost Serverless Architecture** for mobile smartphones.

---

## Architecture Overview

```
                          ┌─────────────────────────────┐
                          │    Mobile Smartphone        │
                          │   (PWA / Home Screen App)   │
                          └──────────────┬──────────────┘
                                         │ HTTPS
                                         ▼
                          ┌─────────────────────────────┐
                          │   Vercel (Hobby Tier: $0)   │
                          │   Next.js 14 App Router     │
                          └──────────────┬──────────────┘
                                         │
                   ┌─────────────────────┴─────────────────────┐
                   │                                           │
                   ▼                                           ▼
    ┌─────────────────────────────┐             ┌─────────────────────────────┐
    │  Render (Free Web Service)  │             │   Supabase (Free Tier: $0)  │
    │   FastAPI (< 512MB RAM)     │◄───────────►│  PostgreSQL Precomputed DB  │
    └─────────────────────────────┘             └──────────────▲──────────────┘
                                                               │
                                                               │ Upserts Precomputed Scores
                                                ┌──────────────┴──────────────┐
                                                │   GitHub Actions (Free Cron)│
                                                │   Mon-Fri 16:00 IST (10:30Z)│
                                                │   daily_bem_update.yml      │
                                                └─────────────────────────────┘
```

---

## Quantitative 100-Point Scoring Model

$$\text{BEM Score} = \text{Price Momentum (25)} + \text{Volume Expansion (20)} + \text{Delivery Strength (15)} + \text{Breakout Quality (15)} + \text{Institutional (10)} + (15 - \text{Exhaustion Score})$$

- **Price Momentum (25 pts)**: 20d return (8 pts), 50d return (5 pts), Nifty 50 Relative Strength (5 pts), Moving Average alignment (4 pts), and 52W High proximity (3 pts).
- **Volume Expansion (20 pts)**: Ratio brackets ($\ge 1.5\times \rightarrow 20, 1.25\text{–}1.5\times \rightarrow 14, 1.0\text{–}1.25\times \rightarrow 10, 0.75\text{–}1.0\times \rightarrow 5$) with distribution trap protection on falling prices.
- **Delivery Strength (15 pts)**: Cash delivery brackets ($>60\% \rightarrow 15, 50\text{–}60\% \rightarrow 13, 40\text{–}50\% \rightarrow 11, 30\text{–}40\% \rightarrow 8, 20\text{–}30\% \rightarrow 5, <20\% \rightarrow 2$).
- **Breakout Quality (15 pts)**: Key resistance breakouts with volume and delivery confirmation.
- **Institutional Flow (10 pts)**: FII/DII net accumulation & Futures Open Interest buildup (Long Buildup, Short Covering, Short Buildup, Long Unwinding).
- **Momentum Exhaustion Adjustment (15 pts)**: Raw score 0–15 evaluating velocity surges, distance from 20 DMA, RSI, and volume tapering. Adds $(15 - \text{Exhaustion Score})$ to score.
- **Chase Alert Engine**: Flags `HIGH CHASE RISK / DO NOT CHASE` on overextended moves and advises structured pullback blueprints.
- **Action Engine**: Computes non-arbitrary ATR Stop Losses, Preferred Buy Zones, Multi-tier Targets (T1, T2, Stretch), and verified $\ge 2:1$ Risk/Reward ratios.

---

## 3-Step Zero-Cost Production Deployment

### Step 1: Push Code to GitHub

```bash
git init
git add .
git commit -m "feat: BEM 100 v2.0 platform"
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```

### Step 2: Deploy Backend to Render (Free Web Service)

1. Sign up / Log in to [render.com](https://render.com).
2. Click **New +** ➔ **Web Service**.
3. Connect your GitHub repository.
4. Render automatically reads `render.yaml` and `backend/Dockerfile`:
   - **Environment**: Docker
   - **Plan**: Free (512MB RAM)
   - **Port**: `8000`
5. Once deployed, note your public backend URL (e.g., `https://bem-100-engine.onrender.com`).

### Step 3: Deploy Frontend to Vercel (Free Hobby Tier)

1. Sign up / Log in to [vercel.com](https://vercel.com).
2. Click **Add New...** ➔ **Project**.
3. Import your GitHub repository.
4. In Project Settings:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Next.js
   - **Environment Variables**:
     - `NEXT_PUBLIC_API_URL` = `https://bem-100-engine.onrender.com` (your Render backend URL)
5. Click **Deploy**. Vercel will generate your live production URL (e.g., `https://bem-100.vercel.app`).

---

## Optional: Connect Supabase PostgreSQL (Free Tier)

1. Create a free project at [supabase.com](https://supabase.com).
2. Go to **SQL Editor** and execute [database/schema.sql](file:///c:/Users/katka/Documents/StockMarket_WatchKeeper/database/schema.sql).
3. In your GitHub repository settings, add secrets:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
4. The daily cron in [.github/workflows/daily_bem_update.yml](file:///c:/Users/katka/Documents/StockMarket_WatchKeeper/.github/workflows/daily_bem_update.yml) will automatically commit precomputed scores every day post-market at 16:00 IST (10:30 UTC).

---

## Mobile PWA Installation Instructions

Open your Vercel URL on a mobile device:

- **iOS (iPhone Safari)**:
  1. Open `https://your-app.vercel.app` in Safari.
  2. Tap the **Share** button (box with arrow up) at the bottom.
  3. Scroll and select **"Add to Home Screen"**.
  4. Tap **Add**.

- **Android (Chrome / Edge)**:
  1. Open `https://your-app.vercel.app` in Chrome or Edge.
  2. Tap the **Three Dots (⋮)** menu in the upper right.
  3. Tap **"Install app"** or **"Add to Home Screen"**.

The application will launch full-screen with offline caching and native app behavior!
