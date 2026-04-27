"""Schema designer — converts project specs into table/relationship models."""
from neon_db_designer.models import (
    Column,
    ColumnType,
    Index,
    ProjectSpec,
    Relationship,
    RelationshipType,
    Schema,
    Table,
)


class SchemaDesigner:
    """Converts ProjectSpec into a NeonDB Schema with tables and relationships.

    Usage:
        designer = SchemaDesigner()
        schema = designer.generate_schema(ProjectSpec(...))
    """

    def generate_schema(self, spec: ProjectSpec) -> Schema:
        schema = Schema()
        self._add_core_extensions(schema)
        self._build_tables_from_spec(schema, spec)
        self._infer_relationships(schema, spec)
        return schema

    def _add_core_extensions(self, schema: Schema) -> None:
        schema.extensions = ["uuid-ossp", "pg_trgm"]

    def _build_tables_from_spec(self, schema: Schema, spec: ProjectSpec) -> None:
        if spec.needs_auth:
            schema.add_table(self._create_users_table(spec))
            schema.add_table(self._create_sessions_table())

        if spec.models:
            for model in spec.models:
                self._add_table_from_model(schema, model)

        if not spec.models and not spec.needs_auth:
            schema.add_table(self._create_default_items_table(spec))

        if spec.needs_multitenancy:
            schema.add_table(self._create_tenants_table())
            self._add_tenant_foreign_keys(schema)

    def _create_users_table(self, spec: ProjectSpec) -> Table:
        table = Table(name="users", comment="User accounts and authentication")
        table.add_column(Column("id", ColumnType.UUID, primary_key=True, default="uuid_generate_v4()"))
        table.add_column(Column("email", ColumnType.VARCHAR, nullable=False, unique=True))
        table.add_column(Column("password_hash", ColumnType.VARCHAR, nullable=False))
        table.add_column(Column("name", ColumnType.VARCHAR))
        table.add_column(Column("role", ColumnType.VARCHAR, default="'user'"))
        table.add_column(Column("created_at", ColumnType.TIMESTAMP, default="NOW()", nullable=False))
        table.add_column(Column("updated_at", ColumnType.TIMESTAMP, default="NOW()", nullable=False))
        table.add_index(Index("idx_users_email", ["email"], unique=True))
        table.add_index(Index("idx_users_created_at", ["created_at"]))
        return table

    def _create_sessions_table(self) -> Table:
        table = Table(name="sessions", comment="User session management")
        table.add_column(Column("id", ColumnType.UUID, primary_key=True, default="uuid_generate_v4()"))
        table.add_column(Column("user_id", ColumnType.UUID, nullable=False, references="users(id)"))
        table.add_column(Column("token_hash", ColumnType.VARCHAR, nullable=False))
        table.add_column(Column("expires_at", ColumnType.TIMESTAMP, nullable=False))
        table.add_column(Column("created_at", ColumnType.TIMESTAMP, default="NOW()", nullable=False))
        table.add_index(Index("idx_sessions_user_id", ["user_id"]))
        table.add_index(Index("idx_sessions_token_hash", ["token_hash"], unique=True))
        return table

    def _create_tenants_table(self) -> Table:
        table = Table(name="tenants", comment="Multi-tenant organizations")
        table.add_column(Column("id", ColumnType.UUID, primary_key=True, default="uuid_generate_v4()"))
        table.add_column(Column("name", ColumnType.VARCHAR, nullable=False))
        table.add_column(Column("slug", ColumnType.VARCHAR, nullable=False, unique=True))
        table.add_column(Column("plan", ColumnType.VARCHAR, default="'free'"))
        table.add_column(Column("created_at", ColumnType.TIMESTAMP, default="NOW()", nullable=False))
        table.add_index(Index("idx_tenants_slug", ["slug"], unique=True))
        return table

    def _add_tenant_foreign_keys(self, schema: Schema) -> None:
        for table in schema.tables:
            if table.name not in ("tenants",):
                table.add_column(Column("tenant_id", ColumnType.UUID, references="tenants(id)", nullable=True))
                table.add_index(Index(f"idx_{table.name}_tenant_id", ["tenant_id"]))

    def _create_default_items_table(self, spec: ProjectSpec) -> Table:
        table = Table(name="items", comment=f"Default entity table for {spec.name}")
        table.add_column(Column("id", ColumnType.UUID, primary_key=True, default="uuid_generate_v4()"))
        table.add_column(Column("name", ColumnType.VARCHAR, nullable=False))
        table.add_column(Column("description", ColumnType.TEXT))
        table.add_column(Column("created_at", ColumnType.TIMESTAMP, default="NOW()", nullable=False))
        table.add_column(Column("updated_at", ColumnType.TIMESTAMP, default="NOW()", nullable=False))
        table.add_index(Index("idx_items_name", ["name"]))
        return table

    def _add_table_from_model(self, schema: Schema, model: dict) -> None:
        name = model.get("name")
        if not name:
            return
        table = Table(name=name, comment=model.get("comment"))
        for col_def in model.get("columns", []):
            col = Column(
                name=col_def["name"],
                col_type=ColumnType[col_def.get("type", "VARCHAR").upper()],
                nullable=col_def.get("nullable", True),
                primary_key=col_def.get("primary_key", False),
                unique=col_def.get("unique", False),
                default=col_def.get("default"),
                references=col_def.get("references"),
            )
            table.add_column(col)

        for idx in model.get("indexes", []):
            table.add_index(Index(idx["name"], idx["columns"], unique=idx.get("unique", False)))

        if not any(c.primary_key for c in table.columns):
            table.add_column(Column("id", ColumnType.UUID, primary_key=True, default="uuid_generate_v4()"))

        schema.add_table(table)

    def _infer_relationships(self, schema: Schema, spec: ProjectSpec) -> None:
        for table in schema.tables:
            for col in table.columns:
                if col.references and "(" in col.references:
                    ref_table, ref_col = col.references.rstrip(")").split("(")
                    schema.relationships.append(
                        Relationship(
                            from_table=table.name,
                            to_table=ref_table,
                            relationship_type=RelationshipType.ONE_TO_MANY,
                            from_column=col.name,
                            to_column=ref_col,
                        )
                    )

        if spec.needs_multitenancy:
            for table in schema.tables:
                if table.name not in ("tenants",) and any(c.name == "tenant_id" for c in table.columns):
                    tenant_table = schema.get_table("tenants")
                    if tenant_table:
                        schema.relationships.append(
                            Relationship(
                                from_table=table.name,
                                to_table="tenants",
                                relationship_type=RelationshipType.MANY_TO_ONE,
                                from_column="tenant_id",
                                to_column="id",
                            )
                        )
