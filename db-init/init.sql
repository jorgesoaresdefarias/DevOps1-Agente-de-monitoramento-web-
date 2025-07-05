CREATE TABLE IF NOT EXISTS ping_results (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP,
    target TEXT,
    value1 FLOAT,  
    value2 FLOAT   
);

CREATE TABLE IF NOT EXISTS http_results (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP,
    target TEXT,
    value1 FLOAT,  
    value2 INT     
);

CREATE TABLE IF NOT EXISTS viaipe_stats (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP,
    cliente TEXT,
    disponibilidade FLOAT,
    banda_consumo FLOAT,
    qualidade FLOAT
);