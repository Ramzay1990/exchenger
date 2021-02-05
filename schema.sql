DROP TABLE IF EXISTS exchange;

CREATE TABLE exchange (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    currency_to TEXT NOT NULL,
    rates FLOAT NOT NULL,
    amount FLOAT NOT NULL,
    result FLOAT NOT NULL
);