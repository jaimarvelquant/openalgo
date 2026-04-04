CREATE TABLE strategy_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    instance_name TEXT,
    symbol TEXT,
    expiry TEXT,
    start_time TEXT,
    squareoff_time TEXT,
    end_time TEXT,
    straddle_width REAL,   -- NEW FIELD
    status TEXT,
    created_at TEXT,
    updated_at TEXT
, leg1 TEXT, leg2 TEXT, enabled INTEGER DEFAULT 0, started_at TEXT, finished_at TEXT)