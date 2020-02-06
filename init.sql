DROP TABLE IF EXISTS ram CASCADE;
DROP TABLE IF EXISTS disk CASCADE;
DROP TABLE IF EXISTS cpu CASCADE;
DROP TABLE IF EXISTS swap CASCADE;
DROP TABLE IF EXISTS network CASCADE;

CREATE TABLE IF NOT EXISTS ram (
    id SERIAL PRIMARY KEY,
    ctime TIME DEFAULT LOCALTIME,
    total NUMERIC,
    available NUMERIC,
    used NUMERIC,
    free NUMERIC,
    percent NUMERIC
);
CREATE TABLE cpu (
    id SERIAL PRIMARY KEY,
    ctime TIME DEFAULT LOCALTIME,
    percent NUMERIC,
    idle NUMERIC,
    system NUMERIC,
    usr NUMERIC
);
CREATE TABLE disk (id SERIAL PRIMARY KEY,
    ctime TIME DEFAULT LOCALTIME,
    device TEXT,
    mountpoint TEXT,
    total NUMERIC,
    used NUMERIC,
    free NUMERIC,
    percent NUMERIC
);
CREATE TABLE swap (
    id SERIAL PRIMARY KEY,
    ctime TIME DEFAULT LOCALTIME,
    total NUMERIC,
    used NUMERIC,
    free NUMERIC,
    percent NUMERIC
);
CREATE TABLE network (
    id SERIAL PRIMARY KEY,
    ctime TIME DEFAULT LOCALTIME,
    bytes_sent NUMERIC,
    bytes_recv NUMERIC
);