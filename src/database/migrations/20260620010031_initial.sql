-- Migration: initial

CREATE TABLE IF NOT EXISTS investments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    classification TEXT,
    code TEXT NOT NULL,
    extended_negotiation REAL,
    extended_negotiation_percentage REAL,
    previous REAL NOT NULL,
    current_price REAL,
    variation_percentage REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);