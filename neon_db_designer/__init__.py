"""NeonDB schema designer and migration system.

Generates PostgreSQL (NeonDB) schema designs from application data models
and feature requirements. Integrates as a pipeline step after frontend and
backend generation.

Usage:
    from neon_db_designer import SchemaDesigner, ProjectSpec
    from neon_db_designer.pipeline import NeonDBPipelineStep, run_from_project_spec

    # Design a schema from a project spec
    spec = ProjectSpec(name="TaskApp", description="Task management", features=["auth"])
    designer = SchemaDesigner()
    schema = designer.generate_schema(spec)

    # Run the full pipeline (migrations + seed data + ORM models)
    result = NeonDBPipelineStep().run(project_dir=".", project_spec=spec)

    # Or via CLI
    # python -m neon_db_designer.cli --name TaskApp --description "Task management"
"""
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
from neon_db_designer.schemas.schema_designer import SchemaDesigner
from neon_db_designer.migrations.migration_generator import MigrationGenerator
from neon_db_designer.seed_data.seed_generator import SeedDataGenerator
from neon_db_designer.orm.orm_generator import ORMGenerator
from neon_db_designer.pipeline import NeonDBPipelineStep, PipelineResult, run_from_project_spec

__all__ = [
    "Column",
    "ColumnType",
    "Index",
    "MigrationGenerator",
    "NeonDBPipelineStep",
    "ORMGenerator",
    "PipelineResult",
    "ProjectSpec",
    "Relationship",
    "RelationshipType",
    "Schema",
    "SchemaDesigner",
    "SeedDataGenerator",
    "run_from_project_spec",
]
