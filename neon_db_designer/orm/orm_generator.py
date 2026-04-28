"""ORM setup generator — produces SQLAlchemy model files from a Schema."""
from neon_db_designer.models import ColumnType, Schema, Table


class ORMGenerator:
    """Generates SQLAlchemy ORM model files from a Schema.

    Usage:
        gen = ORMGenerator()
        files = gen.generate_orm_models(schema, output_dir="db/models")
        # files is a dict mapping filename -> Python model content
    """

    def generate_orm_models(self, schema: Schema, output_dir: str = "db/models") -> dict[str, str]:
        files = {}
        files[f"{output_dir}/__init__.py"] = self._generate_init(schema)
        files[f"{output_dir}/base.py"] = self._generate_base()
        files[f"{output_dir}/database.py"] = self._generate_database()
        for table in schema.tables:
            files[f"{output_dir}/{table.name}.py"] = self._generate_model_file(table)
        return files

    def _to_python_type(self, col_type: ColumnType) -> str:
        mapping = {
            ColumnType.SERIAL: "int",
            ColumnType.BIGSERIAL: "int",
            ColumnType.UUID: "str",
            ColumnType.VARCHAR: "str",
            ColumnType.TEXT: "str",
            ColumnType.INTEGER: "int",
            ColumnType.BIGINT: "int",
            ColumnType.SMALLINT: "int",
            ColumnType.BOOLEAN: "bool",
            ColumnType.DECIMAL: "float",
            ColumnType.NUMERIC: "float",
            ColumnType.REAL: "float",
            ColumnType.DOUBLE_PRECISION: "float",
            ColumnType.TIMESTAMP: "datetime.datetime",
            ColumnType.TIMESTAMP_TZ: "datetime.datetime",
            ColumnType.DATE: "datetime.date",
            ColumnType.TIME: "datetime.time",
            ColumnType.TIME_TZ: "datetime.time",
            ColumnType.JSON: "dict",
            ColumnType.JSONB: "dict",
            ColumnType.ARRAY: "list",
            ColumnType.TSVECTOR: "str",
        }
        return mapping.get(col_type, "str")

    def _sa_type_name(self, col_type: ColumnType) -> str:
        mapping = {
            ColumnType.SERIAL: "Integer",
            ColumnType.BIGSERIAL: "BigInteger",
            ColumnType.UUID: "Uuid",
            ColumnType.VARCHAR: "String",
            ColumnType.TEXT: "Text",
            ColumnType.INTEGER: "Integer",
            ColumnType.BIGINT: "BigInteger",
            ColumnType.SMALLINT: "SmallInteger",
            ColumnType.BOOLEAN: "Boolean",
            ColumnType.DECIMAL: "Numeric",
            ColumnType.NUMERIC: "Numeric",
            ColumnType.REAL: "Float",
            ColumnType.DOUBLE_PRECISION: "Float",
            ColumnType.TIMESTAMP: "DateTime",
            ColumnType.TIMESTAMP_TZ: "DateTime",
            ColumnType.DATE: "Date",
            ColumnType.TIME: "Time",
            ColumnType.TIME_TZ: "Time",
            ColumnType.JSON: "JSON",
            ColumnType.JSONB: "JSON",
            ColumnType.ARRAY: "Array",
            ColumnType.TSVECTOR: "TSVECTOR",
        }
        return mapping.get(col_type, "String")

    def _generate_init(self, schema: Schema) -> str:
        all_classes = ", ".join(self._class_name(t.name) for t in schema.tables)
        init_content = "\n".join(
            f"from .{t.name} import {self._class_name(t.name)}"
            for t in schema.tables
        )
        return (
            '"""Generated SQLAlchemy ORM models."""\n'
            "from .base import Base\n"
            "from .database import engine, SessionLocal, get_db\n"
            + init_content
            + "\n\n"
            f'__all__ = ["Base", "engine", "SessionLocal", "get_db", {all_classes!r}]\n'
        )

    def _generate_base(self) -> str:
        return '''\
"""SQLAlchemy base configuration."""
from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass
'''

    def _generate_database(self) -> str:
        return '''\
"""Database connection and session management."""
from __future__ import annotations

import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/aiwa",
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=os.getenv("SQLALCHEMY_ECHO", "0") == "1",
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency for FastAPI to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''

    def _class_name(self, table_name: str) -> str:
        return "".join(word.capitalize() for word in table_name.split("_"))

    def _generate_model_file(self, table: Table) -> str:
        imports = ["from __future__ import annotations", "from datetime import datetime, date, time", "from uuid import UUID", "import enum"]
        sa_imports = ["from sqlalchemy import Column, ForeignKey, Index, UniqueConstraint, CheckConstraint"]
        orm_imports = ["from sqlalchemy.orm import relationship"]
        model_imports = ["from .base import Base"]

        if table.name == "users":
            imports.append("import passlib.context")

        lines = imports + [""] + sa_imports + orm_imports + model_imports + [""]

        class_name = self._class_name(table.name)
        lines.append(f"class {class_name}(Base):")
        lines.append(f'    """Generated model for table: {table.name}"""')
        lines.append(f"    __tablename__ = {table.name!r}")

        # Columns
        for col in table.columns:
            py_type = self._to_python_type(col.col_type)
            nullable_str = "" if col.nullable else ", nullable=False"
            primary_key_str = ", primary_key=True" if col.primary_key else ""
            unique_str = ", unique=True" if col.unique and not col.primary_key else ""

            if col.references:
                fk_str = f", ForeignKey({col.references!r})"
            else:
                fk_str = ""

            sa_type = self._sa_type_name(col.col_type)
            if col.col_type in (ColumnType.VARCHAR, ColumnType.UUID):
                sa_str = f"{sa_type}(255)"
            elif col.col_type == ColumnType.ARRAY:
                sa_str = f"Array({sa_type})"
            else:
                sa_str = sa_type

            lines.append(
                f"    {col.name} = Column({sa_str}{nullable_str}{primary_key_str}{unique_str}{fk_str})"
            )

        # Indexes
        for idx in table.indexes:
            col_list = ", ".join(f'"{c}"' for c in idx.columns)
            unique_str = ", unique=True" if idx.unique else ""
            lines.append(f"    __table_args__ = (Index({idx.name!r}, {col_list}{unique_str}),)")

        # Table comment
        if table.comment:
            lines.append(f"    __table_args__ = ()  # comment: {table.comment}")

        # Relationships
        for col in table.columns:
            if col.references:
                ref_table = col.references.split("(")[0]
                rel_name = ref_table
                lines.append(f"    {rel_name} = relationship({rel_name!r}, back_populates={table.name!r})")

        return "\n".join(lines) + "\n"
