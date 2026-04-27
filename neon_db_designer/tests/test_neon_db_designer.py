"""Tests for the NeonDB schema designer module."""
from neon_db_designer.models import Column, ColumnType, Index, ProjectSpec, Schema, Table
from neon_db_designer.schemas.schema_designer import SchemaDesigner
from neon_db_designer.migrations.migration_generator import MigrationGenerator
from neon_db_designer.seed_data.seed_generator import SeedDataGenerator
from neon_db_designer.orm.orm_generator import ORMGenerator
from neon_db_designer.pipeline import NeonDBPipelineStep


class TestColumn:
    def test_sql_definition_basic(self):
        col = Column("name", ColumnType.VARCHAR, nullable=False)
        assert col.sql_definition() == '"name" VARCHAR(255) NOT NULL'

    def test_sql_definition_primary_key(self):
        col = Column("id", ColumnType.UUID, primary_key=True, default="uuid_generate_v4()")
        assert "PRIMARY KEY" in col.sql_definition()

    def test_sql_definition_with_reference(self):
        col = Column("user_id", ColumnType.UUID, references="users(id)", nullable=False)
        assert "REFERENCES users(id)" in col.sql_definition()


class TestTable:
    def test_primary_key_column(self):
        table = Table("test_table")
        table.add_column(Column("id", ColumnType.UUID, primary_key=True))
        table.add_column(Column("name", ColumnType.VARCHAR))
        assert table.primary_key_column().name == "id"


class TestProjectSpec:
    def test_needs_auth_true(self):
        spec = ProjectSpec(name="App", description="Login app", features=[])
        assert spec.needs_auth is True

    def test_needs_auth_false(self):
        spec = ProjectSpec(name="App", description="Blog app", features=["blog posts"])
        assert spec.needs_auth is False

    def test_needs_multitenancy_true(self):
        spec = ProjectSpec(name="App", description="Org app", features=["multi-tenant workspace"])
        assert spec.needs_multitenancy is True

    def test_needs_multitenancy_false(self):
        spec = ProjectSpec(name="App", description="Simple app", features=[])
        assert spec.needs_multitenancy is False


class TestSchemaDesigner:
    def test_generate_schema_auth_features_creates_users_and_sessions(self):
        spec = ProjectSpec(
            name="TestApp",
            description="Login and task management",
            features=["user login", "sessions"],
        )
        schema = SchemaDesigner().generate_schema(spec)
        table_names = [t.name for t in schema.tables]
        assert "users" in table_names
        assert "sessions" in table_names

    def test_generate_schema_includes_extensions(self):
        spec = ProjectSpec(name="TestApp", description="A simple app", features=[])
        schema = SchemaDesigner().generate_schema(spec)
        assert "uuid-ossp" in schema.extensions

    def test_generate_schema_explicit_models(self):
        spec = ProjectSpec(
            name="TestApp",
            description="A blog",
            features=[],
            models=[{"name": "posts", "columns": [{"name": "title", "type": "VARCHAR"}]}],
        )
        schema = SchemaDesigner().generate_schema(spec)
        table_names = [t.name for t in schema.tables]
        assert "posts" in table_names

    def test_generate_schema_infers_relationships(self):
        spec = ProjectSpec(
            name="TestApp",
            description="App with posts",
            features=[],
            models=[
                {
                    "name": "users",
                    "columns": [
                        {"name": "id", "type": "UUID", "primary_key": True},
                        {"name": "email", "type": "VARCHAR"},
                    ],
                },
                {
                    "name": "posts",
                    "columns": [
                        {"name": "id", "type": "UUID", "primary_key": True},
                        {"name": "user_id", "type": "UUID", "references": "users(id)"},
                        {"name": "title", "type": "VARCHAR"},
                    ],
                },
            ],
        )
        schema = SchemaDesigner().generate_schema(spec)
        assert len(schema.relationships) > 0


class TestMigrationGenerator:
    def test_generate_migrations_creates_revision_file(self):
        spec = ProjectSpec(
            name="TestApp",
            description="A simple app",
            features=["user accounts"],
            models=[{"name": "items", "columns": [{"name": "name", "type": "VARCHAR"}]}],
        )
        schema = SchemaDesigner().generate_schema(spec)
        files = MigrationGenerator().generate_migrations(schema, output_dir="db/migrations")
        sql_files = [f for f in files if f.endswith(".sql")]
        assert len(sql_files) >= 1
        for path, content in files.items():
            assert len(content) > 0

    def test_create_table_sql_includes_primary_key(self):
        table = Table("test_table")
        table.add_column(Column("id", ColumnType.UUID, primary_key=True, default="uuid_generate_v4()"))
        table.add_column(Column("name", ColumnType.VARCHAR, nullable=False))
        sql = MigrationGenerator()._create_table_sql(table)
        assert "CREATE TABLE" in sql
        assert "PRIMARY KEY" in sql


class TestSeedDataGenerator:
    def test_generate_seed_data(self):
        spec = ProjectSpec(
            name="TestApp",
            description="App with users",
            features=["user accounts"],
        )
        schema = SchemaDesigner().generate_schema(spec)
        sql = SeedDataGenerator().generate_seed_data(schema)
        assert "INSERT INTO" in sql
        assert '"users"' in sql or "'users'" in sql


class TestORMGenerator:
    def test_generate_orm_models(self):
        spec = ProjectSpec(
            name="TestApp",
            description="A simple app",
            features=[],
            models=[{"name": "items", "columns": [{"name": "name", "type": "VARCHAR"}]}],
        )
        schema = SchemaDesigner().generate_schema(spec)
        files = ORMGenerator().generate_orm_models(schema, output_dir="db/models")
        assert len(files) >= 3
        assert "db/models/__init__.py" in files
        assert "db/models/base.py" in files
        for path, content in files.items():
            assert len(content) > 0

    def test_model_file_includes_class_definition(self):
        table = Table("items")
        table.add_column(Column("id", ColumnType.UUID, primary_key=True, default="uuid_generate_v4()"))
        table.add_column(Column("name", ColumnType.VARCHAR, nullable=False))
        content = ORMGenerator()._generate_model_file(table)
        assert "class Items" in content
        assert "__tablename__ = 'items'" in content


class TestNeonDBPipelineStep:
    def test_run_produces_files(self, tmp_path):
        spec = ProjectSpec(
            name="TestApp",
            description="A task app",
            features=["user accounts", "task management"],
        )
        step = NeonDBPipelineStep()
        result = step.run(project_dir=str(tmp_path), project_spec=spec)
        assert result.success is True
        assert len(result.files_written) > 0
        for f in result.files_written:
            assert (tmp_path / f).exists()

    def test_run_with_explicit_models(self, tmp_path):
        spec = ProjectSpec(
            name="BlogApp",
            description="A blog app",
            features=[],
            models=[
                {
                    "name": "posts",
                    "columns": [
                        {"name": "title", "type": "VARCHAR"},
                        {"name": "content", "type": "TEXT"},
                    ],
                },
            ],
        )
        step = NeonDBPipelineStep()
        result = step.run(project_dir=str(tmp_path), project_spec=spec)
        assert result.success is True
        schema_json = (tmp_path / "db" / "schema.json").read_text()
        import json
        data = json.loads(schema_json)
        assert any(t["name"] == "posts" for t in data["tables"])
