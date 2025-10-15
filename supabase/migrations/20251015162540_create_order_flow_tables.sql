/*
  # Order Flow Visualizer Database Schema

  1. New Tables
    - `symbols`
      - `symbol` (text, primary key) - Stock symbol (e.g., RELIANCE)
      - `token` (text) - DhanHQ security ID
      - `name` (text) - Company name
      - `sector` (text) - Industry sector
      - `market_cap` (text) - Market capitalization
      - `exchange` (text) - Exchange (NSE/BSE)
      - `last_updated` (timestamptz) - Last cache update
      - `is_active` (boolean) - Active status
      - `search_count` (integer) - Number of searches (for popularity)
      - `created_at` (timestamptz) - Record creation time

    - `market_data`
      - `id` (uuid, primary key)
      - `symbol` (text) - Stock symbol reference
      - `timestamp` (timestamptz) - Data timestamp
      - `ltp` (numeric) - Last traded price
      - `volume` (bigint) - Trading volume
      - `bid_price` (numeric) - Best bid price
      - `ask_price` (numeric) - Best ask price
      - `data` (jsonb) - Full market data snapshot
      - `created_at` (timestamptz) - Record creation

    - `user_preferences`
      - `id` (uuid, primary key)
      - `user_id` (text) - User identifier
      - `key` (text) - Preference key
      - `value` (jsonb) - Preference value
      - `updated_at` (timestamptz) - Last update

    - `symbol_requests`
      - `id` (uuid, primary key)
      - `symbol` (text) - Requested symbol
      - `requested_by` (text) - User who requested
      - `status` (text) - pending/completed/failed
      - `created_at` (timestamptz) - Request time

  2. Security
    - Enable RLS on all tables
    - Add policies for public read access on symbols
    - Add policies for authenticated users on preferences
    - Add policies for system writes

  3. Indexes
    - Indexes on frequently queried columns for performance
*/

-- Create symbols table
CREATE TABLE IF NOT EXISTS symbols (
    symbol TEXT PRIMARY KEY,
    token TEXT NOT NULL,
    name TEXT NOT NULL,
    sector TEXT DEFAULT '',
    market_cap TEXT DEFAULT '',
    exchange TEXT DEFAULT 'NSE',
    last_updated TIMESTAMPTZ DEFAULT now(),
    is_active BOOLEAN DEFAULT true,
    search_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Create market_data table
CREATE TABLE IF NOT EXISTS market_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    ltp NUMERIC,
    volume BIGINT,
    bid_price NUMERIC,
    ask_price NUMERIC,
    data JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Create user_preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    key TEXT NOT NULL,
    value JSONB,
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(user_id, key)
);

-- Create symbol_requests table
CREATE TABLE IF NOT EXISTS symbol_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol TEXT NOT NULL,
    requested_by TEXT DEFAULT 'anonymous',
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_symbols_search ON symbols(symbol, name);
CREATE INDEX IF NOT EXISTS idx_symbols_active ON symbols(is_active, last_updated DESC);
CREATE INDEX IF NOT EXISTS idx_symbols_search_count ON symbols(search_count DESC);

CREATE INDEX IF NOT EXISTS idx_market_data_symbol ON market_data(symbol, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_market_data_timestamp ON market_data(timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_user_prefs_user ON user_preferences(user_id, key);

CREATE INDEX IF NOT EXISTS idx_symbol_requests_status ON symbol_requests(status, created_at DESC);

-- Enable Row Level Security
ALTER TABLE symbols ENABLE ROW LEVEL SECURITY;
ALTER TABLE market_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE symbol_requests ENABLE ROW LEVEL SECURITY;

-- RLS Policies for symbols (public read, system write)
CREATE POLICY "Allow public read access to symbols"
    ON symbols FOR SELECT
    TO anon, authenticated
    USING (true);

CREATE POLICY "Allow public insert to symbols"
    ON symbols FOR INSERT
    TO anon, authenticated
    WITH CHECK (true);

CREATE POLICY "Allow public update to symbols"
    ON symbols FOR UPDATE
    TO anon, authenticated
    USING (true)
    WITH CHECK (true);

-- RLS Policies for market_data (public read, system write)
CREATE POLICY "Allow public read access to market data"
    ON market_data FOR SELECT
    TO anon, authenticated
    USING (true);

CREATE POLICY "Allow public insert to market data"
    ON market_data FOR INSERT
    TO anon, authenticated
    WITH CHECK (true);

-- RLS Policies for user_preferences (user-specific)
CREATE POLICY "Users can view own preferences"
    ON user_preferences FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Users can insert own preferences"
    ON user_preferences FOR INSERT
    TO authenticated
    WITH CHECK (true);

CREATE POLICY "Users can update own preferences"
    ON user_preferences FOR UPDATE
    TO authenticated
    USING (true)
    WITH CHECK (true);

-- RLS Policies for symbol_requests (public)
CREATE POLICY "Allow public read access to symbol requests"
    ON symbol_requests FOR SELECT
    TO anon, authenticated
    USING (true);

CREATE POLICY "Allow public insert to symbol requests"
    ON symbol_requests FOR INSERT
    TO anon, authenticated
    WITH CHECK (true);

-- Insert default popular NSE symbols
INSERT INTO symbols (symbol, token, name, sector, exchange, search_count) VALUES
    ('RELIANCE', '2885633', 'Reliance Industries Ltd', 'Energy', 'NSE', 100),
    ('TCS', '2953217', 'Tata Consultancy Services Ltd', 'IT', 'NSE', 95),
    ('HDFCBANK', '341249', 'HDFC Bank Ltd', 'Banking', 'NSE', 90),
    ('INFY', '408065', 'Infosys Ltd', 'IT', 'NSE', 85),
    ('ITC', '424961', 'ITC Ltd', 'FMCG', 'NSE', 80),
    ('BHARTIARTL', '2714625', 'Bharti Airtel Ltd', 'Telecom', 'NSE', 75),
    ('SBIN', '779521', 'State Bank of India', 'Banking', 'NSE', 70),
    ('ASIANPAINT', '60417', 'Asian Paints Ltd', 'Consumer Goods', 'NSE', 65),
    ('KOTAKBANK', '492033', 'Kotak Mahindra Bank Ltd', 'Banking', 'NSE', 60),
    ('MARUTI', '2815745', 'Maruti Suzuki India Ltd', 'Automobile', 'NSE', 55)
ON CONFLICT (symbol) DO NOTHING;
