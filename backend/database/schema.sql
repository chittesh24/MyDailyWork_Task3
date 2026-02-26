-- Database schema for Image Captioning System
-- PostgreSQL

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
);

CREATE INDEX idx_users_email ON users(email);

-- API Keys table
CREATE TABLE IF NOT EXISTS api_keys (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    hashed_key VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100) DEFAULT 'Default Key',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP WITH TIME ZONE,
    is_active INTEGER DEFAULT 1 CHECK (is_active IN (0, 1))
);

CREATE INDEX idx_api_keys_user ON api_keys(user_id);
CREATE INDEX idx_api_keys_hash ON api_keys(hashed_key);

-- Captions table
CREATE TABLE IF NOT EXISTS captions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    image_path VARCHAR(500),
    generated_caption TEXT NOT NULL,
    model_version VARCHAR(50) DEFAULT 'v1.0',
    confidence_score FLOAT,
    inference_time_ms FLOAT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_captions_user ON captions(user_id);
CREATE INDEX idx_captions_timestamp ON captions(timestamp);

-- Usage tracking table
CREATE TABLE IF NOT EXISTS usage (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    daily_request_count INTEGER DEFAULT 0,
    total_requests INTEGER DEFAULT 0,
    last_reset TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_usage_user ON usage(user_id);

-- Function to reset daily counts
CREATE OR REPLACE FUNCTION reset_daily_usage()
RETURNS void AS $$
BEGIN
    UPDATE usage
    SET daily_request_count = 0,
        last_reset = CURRENT_TIMESTAMP
    WHERE last_reset < CURRENT_DATE;
END;
$$ LANGUAGE plpgsql;

-- Comments
COMMENT ON TABLE users IS 'Registered users';
COMMENT ON TABLE api_keys IS 'API keys for authentication (hashed)';
COMMENT ON TABLE captions IS 'Generated caption history';
COMMENT ON TABLE usage IS 'Per-user usage tracking and rate limiting';
