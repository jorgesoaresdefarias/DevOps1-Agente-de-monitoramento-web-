CREATE TABLE IF NOT EXISTS ping_results (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP,
    target TEXT,
    value1 FLOAT,  -- RTT
    value2 FLOAT   -- Packet loss
);

CREATE TABLE IF NOT EXISTS http_results (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP,
    target TEXT,
    value1 FLOAT,  -- Load time (ms)
    value2 INT     -- HTTP Status Code
);
