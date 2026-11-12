CREATE TABLE IF NOT EXISTS predictions (
    id                  SERIAL PRIMARY KEY,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    amount_usd          INTEGER NOT NULL,
    term_months         INTEGER NOT NULL,
    monthly_income_usd  NUMERIC(10, 2) NOT NULL,
    default_probability NUMERIC(5, 4) NOT NULL,
    risk_band           TEXT NOT NULL
);
