"""Core data models for NeonDB schema design."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ColumnType(Enum):
    """PostgreSQL column types supported by NeonDB."""

    SERIAL = "SERIAL"
    BIGSERIAL = "BIGSERIAL"
    UUID = "UUID"
    VARCHAR = "VARCHAR"
    TEXT = "TEXT"
    INTEGER = "INTEGER"
    BIGINT = "BIGINT"
    SMALLINT = "SMALLINT"
    BOOLEAN = "BOOLEAN"
    DECIMAL = "DECIMAL"
    NUMERIC = "NUMERIC"
    REAL = "REAL"
    DOUBLE_PRECISION = "DOUBLE PRECISION"
    TIMESTAMP = "TIMESTAMP"
    TIMESTAMP_TZ = "TIMESTAMP WITH TIME ZONE"
    DATE = "DATE"
    TIME = "TIME"
    TIME_TZ = "TIME WITH TIME ZONE"
    JSON = "JSON"
    JSONB = "JSONB"
    ARRAY = "ARRAY"
    TSVECTOR = "TSVECTOR"


class RelationshipType(Enum):
    ONE_TO_ONE = "one-to-one"
    ONE_TO_MANY = "one-to-many"
    MANY_TO_MANY = "many-to-many"


@dataclass
class Column:
    name: str
    col_type: ColumnType
    nullable: bool = True
    primary_key: bool = False
    unique: bool = False
    default: Optional[str] = None
    references: Optional[str] = None  # table_name.column_name
    check: Optional[str] = None
    array_dimensions: int = 0

    def sql_definition(self) -> str:
        parts = [f'"{self.name}"', self.col_type.value]
        if self.col_type == ColumnType.VARCHAR:
            parts[-1] = f"VARCHAR(255)"
        if self.col_type == ColumnType.ARRAY:
            parts[-1] = f"{parts[-1]}[]"
        if self.primary_key:
            parts.append("PRIMARY KEY")
        if not self.nullable:
            parts.append("NOT NULL")
        if self.unique and not self.primary_key:
            parts.append("UNIQUE")
        if self.default:
            parts.append(f"DEFAULT {self.default}")
        if self.references:
            parts.append(f"REFERENCES {self.references}")
        if self.check:
            parts.append(f"CHECK ({self.check})")
        return " ".join(parts)


@dataclass
class Index:
    name: str
    columns: list[str]
    unique: bool = False
    using: str = "btree"
    where: Optional[str] = None


@dataclass
class Relationship:
    from_table: str
    to_table: str
    relationship_type: RelationshipType
    through_table: Optional[str] = None  # for many-to-many
    from_column: str = "id"
    to_column: str = "id"
    on_delete: str = "CASCADE"


@dataclass
class Table:
    name: str
    columns: list[Column] = field(default_factory=list)
    indexes: list[Index] = field(default_factory=list)
    comment: Optional[str] = None
    raw_sql: Optional[str] = None  # custom SQL for the table body

    def primary_key_column(self) -> Optional[Column]:
        return next((c for c in self.columns if c.primary_key), None)

    def add_column(self, column: Column) -> None:
        self.columns.append(column)

    def add_index(self, index: Index) -> None:
        self.indexes.append(index)


@dataclass
class Schema:
    tables: list[Table] = field(default_factory=list)
    relationships: list[Relationship] = field(default_factory=list)
    extensions: list[str] = field(default_factory=list)
    raw_sql: Optional[str] = field(default=None)  # custom SQL for schema-level

    def add_table(self, table: Table) -> None:
        self.tables.append(table)

    def get_table(self, name: str) -> Optional[Table]:
        return next((t for t in self.tables if t.name == name), None)


@dataclass
class ProjectSpec:
    """A project specification from which to derive a schema."""

    name: str
    description: str
    features: list[str] = field(default_factory=list)
    models: list[dict] = field(default_factory=list)  # explicit model definitions
    tech_stack: dict = field(default_factory=dict)

    @property
    def needs_auth(self) -> bool:
        auth_keywords = {"auth", "login", "user", "account", "session", "password"}
        return (
            any(kw in f.lower() for f in self.features for kw in auth_keywords)
            or any(kw in f.lower() for f in [self.description] for kw in auth_keywords)
        )

    @property
    def needs_multitenancy(self) -> bool:
        mt_keywords = {"tenant", "organization", "team", "workspace", "multi"}
        return any(
            kw in f.lower()
            for f in self.features + [self.description]
            for kw in mt_keywords
        )
