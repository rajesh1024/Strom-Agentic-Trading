-- Create trading database
CREATE DATABASE trading;

-- Connect to trading database
\c trading;

-- Create audit_log table (as per RULES.md)
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    agent_id VARCHAR(255),
    action VARCHAR(255) NOT NULL,
    inputs JSONB,
    outputs JSONB,
    correlation_id VARCHAR(255),
    error TEXT
);

-- Index for correlation_id and timestamp
CREATE INDEX idx_audit_log_correlation_id ON audit_log(correlation_id);
CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp);

-- Create other necessary tables (placeholder)
CREATE TABLE IF NOT EXISTS positions (
    id SERIAL PRIMARY KEY,
    instrument VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL,
    average_price DECIMAL(18, 2) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
