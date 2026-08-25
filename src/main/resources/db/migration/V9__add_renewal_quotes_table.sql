-- V9__add_renewal_quotes_table.sql
CREATE TABLE renewal_quotes (
    id              BIGSERIAL PRIMARY KEY,
    policy_id       BIGINT NOT NULL REFERENCES policy_documents(id),
    base_premium    NUMERIC(10,2) NOT NULL,
    risk_adj_factor NUMERIC(5,4) NOT NULL DEFAULT 1.0000,
    final_premium   NUMERIC(10,2) NOT NULL,
    generated_at    TIMESTAMP NOT NULL DEFAULT NOW(),
    expires_at      TIMESTAMP NOT NULL,
    state_code      VARCHAR(2) NOT NULL,
    coverage_tier   VARCHAR(32) NOT NULL,
    quote_metadata  JSONB,
    CONSTRAINT uq_active_quote UNIQUE (policy_id, expires_at)
);
CREATE INDEX idx_renewal_quotes_policy ON renewal_quotes(policy_id);
CREATE INDEX idx_renewal_quotes_expires ON renewal_quotes(expires_at);

