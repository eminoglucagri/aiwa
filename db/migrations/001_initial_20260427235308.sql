-- Revision: 001_initial
-- Down revision: None
-- Message: initial schema

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS uuid-ossp;

CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Migration SQL
CREATE EXTENSION IF NOT EXISTS uuid-ossp;

CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TABLE "users" (
    "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "password_hash" VARCHAR(255) NOT NULL,
    "name" VARCHAR(255),
    "role" VARCHAR(255) DEFAULT 'user',
    "created_at" TIMESTAMP NOT NULL DEFAULT NOW(),
    "updated_at" TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE INDEX "idx_users_email" USING btree ("email"),
    INDEX "idx_users_created_at" USING btree ("created_at")
);
COMMENT ON TABLE "users" IS 'User accounts and authentication';

CREATE TABLE "sessions" (
    "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "user_id" UUID NOT NULL REFERENCES users(id),
    "token_hash" VARCHAR(255) NOT NULL,
    "expires_at" TIMESTAMP NOT NULL,
    "created_at" TIMESTAMP NOT NULL DEFAULT NOW(),
    INDEX "idx_sessions_user_id" USING btree ("user_id"),
    UNIQUE INDEX "idx_sessions_token_hash" USING btree ("token_hash")
);
COMMENT ON TABLE "sessions" IS 'User session management';

-- Rollback
DROP TABLE IF EXISTS "sessions" CASCADE;

DROP TABLE IF EXISTS "users" CASCADE;

DROP EXTENSION IF EXISTS pg_trgm;

DROP EXTENSION IF EXISTS uuid-ossp;