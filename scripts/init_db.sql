CREATE TABLE test_sessions (
    id SERIAL PRIMARY KEY,
    laptop_serial TEXT,
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMP,
    overall_status TEXT CHECK (overall_status IN ('PASS', 'FAIL'))
);

CREATE TABLE usb_tests (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES test_sessions(id) ON DELETE CASCADE,
    drive TEXT NOT NULL,
    write_speed_mb_s REAL,
    read_speed_mb_s REAL,
    checksum_ok BOOLEAN,
    status TEXT CHECK (status IN ('PASS', 'FAIL')),
    error TEXT
);

CREATE TABLE audio_tests (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES test_sessions(id) ON DELETE CASCADE,
    device_name TEXT,
    channel TEXT CHECK (channel IN ('LEFT', 'RIGHT')),
    status TEXT CHECK (status IN ('PASS', 'FAIL')),
    error TEXT
);