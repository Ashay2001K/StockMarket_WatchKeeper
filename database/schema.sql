-- BEM 100 v2.0 - Supabase PostgreSQL Schema
-- Free Tier Optimized: Minimal storage footprint (< 500MB) with high-speed indexes

-- 1. Stocks Universe Table
CREATE TABLE IF NOT EXISTS stocks (
    symbol VARCHAR(30) PRIMARY KEY,
    company_name VARCHAR(150),
    sector VARCHAR(80),
    market_cap_tier VARCHAR(20) DEFAULT 'Mid/Large', -- LargeCap, MidCap, SmallCap
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 2. Daily Precomputed Scores Table
CREATE TABLE IF NOT EXISTS daily_scores (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(30) NOT NULL REFERENCES stocks(symbol) ON DELETE CASCADE,
    date DATE NOT NULL,
    close_price NUMERIC(12, 2) NOT NULL,
    day_change_pct NUMERIC(6, 2) NOT NULL,
    bem_score NUMERIC(5, 1) NOT NULL,
    action VARCHAR(30) NOT NULL,
    
    -- Component Breakdown
    price_momentum_score NUMERIC(5, 2) NOT NULL,
    volume_expansion_score NUMERIC(5, 2) NOT NULL,
    delivery_score NUMERIC(5, 2) NOT NULL,
    breakout_score NUMERIC(5, 2) NOT NULL,
    institutional_score NUMERIC(5, 2) NOT NULL,
    exhaustion_adjustment NUMERIC(5, 2) NOT NULL,
    raw_exhaustion_score NUMERIC(5, 2) NOT NULL,
    
    -- Chase & Alert Flags
    chase_alert_active BOOLEAN DEFAULT FALSE,
    chase_alert_severity VARCHAR(20) DEFAULT 'NONE',
    chase_alert_reason TEXT,
    
    -- Potential & Setup
    potential_level VARCHAR(20) NOT NULL,
    potential_probability_pct INT NOT NULL,
    preferred_buy_min NUMERIC(12, 2),
    preferred_buy_max NUMERIC(12, 2),
    breakout_entry NUMERIC(12, 2),
    stop_loss NUMERIC(12, 2),
    stop_loss_pct NUMERIC(6, 2),
    target_1 NUMERIC(12, 2),
    target_2 NUMERIC(12, 2),
    stretch_target NUMERIC(12, 2),
    risk_reward_t1 NUMERIC(6, 2),
    risk_reward_t2 NUMERIC(6, 2),
    
    -- Metadata
    confidence VARCHAR(20) DEFAULT 'High',
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    
    CONSTRAINT unique_symbol_date UNIQUE (symbol, date)
);

-- Indexes for instant mobile retrieval (<200ms)
CREATE INDEX IF NOT EXISTS idx_daily_scores_symbol_date ON daily_scores(symbol, date DESC);
CREATE INDEX IF NOT EXISTS idx_daily_scores_date_bem ON daily_scores(date DESC, bem_score DESC);
CREATE INDEX IF NOT EXISTS idx_daily_scores_action ON daily_scores(action);
CREATE INDEX IF NOT EXISTS idx_daily_scores_chase ON daily_scores(chase_alert_active);

-- 3. Watchlists Table
CREATE TABLE IF NOT EXISTS watchlists (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(80) DEFAULT 'default_user',
    symbol VARCHAR(30) NOT NULL REFERENCES stocks(symbol) ON DELETE CASCADE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    CONSTRAINT unique_user_symbol UNIQUE (user_id, symbol)
);

-- 4. Market Regime Table
CREATE TABLE IF NOT EXISTS market_regime (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    regime VARCHAR(30) NOT NULL, -- Risk-On, Risk-Off, Neutral
    nifty_close NUMERIC(12, 2) NOT NULL,
    nifty_above_20dma BOOLEAN DEFAULT TRUE,
    nifty_above_50dma BOOLEAN DEFAULT TRUE,
    nifty_above_200dma BOOLEAN DEFAULT TRUE,
    india_vix NUMERIC(6, 2),
    notes JSONB DEFAULT '[]'::jsonb,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);
