DROP TABLE IF EXISTS users;
CREATE TABLE users(
    id INTEGER DEFAULT 1 PRIMARY KEY AUTOINCREMENT,
    name STRING NOT NULL,
    password STRING NOT NULL
);