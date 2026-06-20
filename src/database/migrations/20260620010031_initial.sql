-- Migration: initial

CREATE TABLE IF NOT EXISTS investments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    name TEXT NOT NULL,
    classification TEXT NOT NULL,
    code TEXT NOT NULL,
    extended_negotiation REAL,
    extended_negotiation_percentage REAL,
    previous REAL,
    variation_percentage REAL
);