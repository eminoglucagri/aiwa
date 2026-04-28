"""Seed data generator — produces SQL INSERT scripts for development data."""
from neon_db_designer.models import Schema, Table


class SeedDataGenerator:
    """Generates SQL seed data from a Schema for development and testing.

    Usage:
        gen = SeedDataGenerator()
        sql = gen.generate_seed_data(schema)
    """

    def generate_seed_data(self, schema: Schema) -> str:
        lines = ["-- Seed data for NeonDB schema"]
        lines.append(f"-- Generated at {__import__('datetime').datetime.utcnow().isoformat()}")
        lines.append("")

        for table in schema.tables:
            sql = self._table_seed_data(table)
            if sql:
                lines.append(sql)
                lines.append("")

        return "\n".join(lines)

    def _table_seed_data(self, table: Table) -> str:
        if table.name == "tenants":
            return self._tenants_seed(table)
        if table.name == "users":
            return self._users_seed(table)
        return self._generic_seed(table)

    def _tenants_seed(self, table: Table) -> str:
        cols = [c.name for c in table.columns]
        return f"""\
INSERT INTO "{table.name}" ({", ".join(f'"{c}"' for c in cols)}) VALUES
    (uuid_generate_v4(), 'Default Organization', 'default-org', 'free', NOW()),
    (uuid_generate_v4(), 'Acme Corp', 'acme-corp', 'pro', NOW())
ON CONFLICT ("slug") DO NOTHING;"""

    def _users_seed(self, table: Table) -> str:
        cols = [c.name for c in table.columns]
        return f"""\
INSERT INTO "{table.name}" ({", ".join(f'"{c}"' for c in cols)}) VALUES
    (uuid_generate_v4(), 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4mVPmiPaG4W4GxOS', 'Admin User', 'admin', NOW(), NOW()),
    (uuid_generate_v4(), 'demo@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4mVPmiPaG4W4GxOS', 'Demo User', 'user', NOW(), NOW())
ON CONFLICT ("email") DO NOTHING;"""

    def _generic_seed(self, table: Table) -> str:
        cols = [c.name for c in table.columns if c.name != "id"]
        if not cols:
            return ""
        sample_values = {
            "name": "'Sample Item'",
            "description": "'A sample description for development purposes'",
            "email": "'sample@example.com'",
            "created_at": "NOW()",
            "updated_at": "NOW()",
        }
        placeholders = [sample_values.get(name, "NULL") for name in cols]
        return f"""\
INSERT INTO "{table.name}" ({", ".join(f'"{c}"' for c in cols)})
SELECT {", ".join(placeholders)}
WHERE NOT EXISTS (SELECT 1 FROM "{table.name}" LIMIT 1);"""
