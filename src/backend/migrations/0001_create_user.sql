CREATE TABLE IF NOT EXISTS users (
                                     id TEXT PRIMARY KEY,
                                     name TEXT NOT NULL,
                                     age INTEGER NOT NULL CHECK(age >= 0),
    is_dev INTEGER NOT NULL DEFAULT 0,
    email TEXT NOT NULL UNIQUE
    );