"""Migration generator — produces Alembic/SQLAlchemy migration files for NeonDB."""
from datetime import datetime
from pathlib import Path

from neon_db_designer.models import Schema, Table


class MigrationGenerator:
    """Generates SQLAlchemy/Alembic-style migration files from a Schema.

    Usage:
        gen = MigrationGenerator()
        files = gen.generate_migrations(schema, output_dir="db/migrations")
        # files is a dict mapping filename -> SQL content
    """

    def generate_migrations(self, schema: Schema, output_dir: str = "db/migrations") -> dict[str, str]:
        revisions = self._build_revisions(schema)
        return self._render_migrations(revisions, output_dir)

    def _build_revisions(self, schema: Schema) -> list[dict]:
        revisions = []

        up_sql_parts = []
        for ext in schema.extensions:
            up_sql_parts.append(f"CREATE EXTENSION IF NOT EXISTS {ext};")
        for table in schema.tables:
            up_sql_parts.append(self._create_table_sql(table))

        down_sql_parts = []
        for table in reversed(schema.tables):
            down_sql_parts.append(f'DROP TABLE IF EXISTS "{table.name}" CASCADE;')
        for ext in reversed(schema.extensions):
            down_sql_parts.append(f"DROP EXTENSION IF EXISTS {ext};")

        revisions.append(
            {
                "revision": "001_initial",
                "down_revision": None,
                "message": "initial schema",
                "up_sql": "\n\n".join(up_sql_parts),
                "down_sql": "\n\n".join(down_sql_parts),
            }
        )

        return revisions

    def _render_migrations(self, revisions: list[dict], output_dir: str) -> dict[str, str]:
        files = {}
        for rev in revisions:
            ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            filename = f"{rev['revision']}_{ts}.sql"
            content = f"-- Revision: {rev['revision']}\n"
            content += f"-- Down revision: {rev['down_revision'] or 'None'}\n"
            content += f"-- Message: {rev['message']}\n\n"
            content += "-- Enable extensions\n"
            for line in rev["up_sql"].split(";\n"):
                stripped = line.strip()
                if "CREATE EXTENSION" in stripped:
                    content += stripped + ";\n\n"
            content += "-- Migration SQL\n"
            content += rev["up_sql"]
            if not rev["up_sql"].endswith(";"):
                content += ";"
            content += "\n\n-- Rollback\n"
            content += rev["down_sql"]
            files[f"{output_dir}/{filename}"] = content

            py_content = self._alembic_revision_file(rev)
            py_filename = f"{output_dir}/versions/{ts}_{rev['revision']}.py"
            files[py_filename] = py_content

        files[f"{output_dir}/env.py"] = self._alembic_env_py()
        files[f"{output_dir}/script.py.mako"] = self._alembic_script_mako()
        files[f"{output_dir}/alembic.ini"] = self._alembic_ini()
        return files

    def _create_table_sql(self, table: Table) -> str:
        lines = [f'CREATE TABLE "{table.name}" (']
        col_lines = []
        for col in table.columns:
            col_lines.append(f"    {col.sql_definition()}")
        for idx in table.indexes:
            col_list = ", ".join(f'"{c}"' for c in idx.columns)
            unique_str = "UNIQUE " if idx.unique else ""
            col_lines.append(f"    {unique_str}INDEX \"{idx.name}\" USING {idx.using} ({col_list})")
        if table.raw_sql:
            col_lines.append(f"    {table.raw_sql}")
        lines.append(",\n".join(col_lines))
        lines.append(");")
        if table.comment:
            lines.append(f"COMMENT ON TABLE \"{table.name}\" IS '{table.comment}';")
        return "\n".join(lines)

    def _alembic_revision_file(self, rev: dict) -> str:
        return (
            f"""\
'''{rev['message']}

Revision ID: {rev['revision']}
Revises: {rev['down_revision']}
Create Date: {datetime.utcnow().isoformat()}

'''
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '{rev['revision']}'
down_revision = {f"'{rev['down_revision']}'" if rev['down_revision'] else 'None'}
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('''{rev['up_sql']}''')


def downgrade() -> None:
    op.execute('''{rev['down_sql']}''')
"""
        )

    def _alembic_env_py(self) -> str:
        return '''\
"""Alembic environment configuration."""
from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Alembic Config object
config = context.config

if config.config_file_name:
    import sys
    sys.path.insert(0, ".")

target_metadata = None


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''

    def _alembic_script_mako(self) -> str:
        return '''\
"""${message}

Revision ID: ${up_revision if up_revision else '(head)'}
Revises: ${down_revision if down_revision else '(base)'}
Create Date: ${create_date}

"""
from __future__ import annotations

from alembic import context
from sqlalchemy import engine_from_config, pool

${imports if imports else ""}

# Alembic Config object
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = None


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''

    def _alembic_ini(self) -> str:
        return """\
[alembic]
script_location = db/migrations
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = postgresql://user:password@host/dbname

[post_write_hooks]

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""
