-- Seed data for NeonDB schema
-- Generated at 2026-04-27T23:53:08.362893

INSERT INTO "users" ("id", "email", "password_hash", "name", "role", "created_at", "updated_at") VALUES
    (uuid_generate_v4(), 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4mVPmiPaG4W4GxOS', 'Admin User', 'admin', NOW(), NOW()),
    (uuid_generate_v4(), 'demo@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4mVPmiPaG4W4GxOS', 'Demo User', 'user', NOW(), NOW())
ON CONFLICT ("email") DO NOTHING;

INSERT INTO "sessions" ("user_id", "token_hash", "expires_at", "created_at")
SELECT NULL, NULL, NULL, NOW()
WHERE NOT EXISTS (SELECT 1 FROM "sessions" LIMIT 1);
