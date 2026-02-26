CREATE TABLE users (
    id          SERIAL PRIMARY KEY,
    username    TEXT UNIQUE NOT NULL,
    password    TEXT NOT NULL 
);

CREATE TABLE channels (
    id          SERIAL PRIMARY KEY,
    name        TEXT UNIQUE NOT NULL,
    password    TEXT        
);

CREATE TABLE messages (
    id          SERIAL PRIMARY KEY,
    channel_id  INTEGER NOT NULL REFERENCES channels(id) ON DELETE CASCADE,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content     TEXT NOT NULL
);

