"""Pipeline integration — orchestrates schema design as a step in the AIWA pipeline."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from neon_db_designer.models import ProjectSpec, Schema
from neon_db_designer.orm.orm_generator import ORMGenerator
from neon_db_designer.schemas.schema_designer import SchemaDesigner
from neon_db_designer.migrations.migration_generator import MigrationGenerator
from neon_db_designer.seed_data.seed_generator import SeedDataGenerator


@dataclass
class PipelineResult:
    """Result of a pipeline step."""

    success: bool
    output_dir: str
    files_written: list[str]
    errors: list[str]


class NeonDBPipelineStep:
    """A single pipeline step that generates NeonDB schema artifacts.

    Integrate as a step after frontend and backend generation:

        from neon_db_designer.pipeline import NeonDBPipelineStep

        step = NeonDBPipelineStep()
        result = step.run(
            project_dir=".",
            project_spec=ProjectSpec(name="MyApp", description="A task app")
        )
    """

    def run(
        self,
        project_dir: str,
        project_spec: ProjectSpec,
        output_base: str = "db",
    ) -> PipelineResult:
        errors = []
        files_written = []

        try:
            designer = SchemaDesigner()
            schema = designer.generate_schema(project_spec)

            mg = MigrationGenerator()
            migration_files = mg.generate_migrations(schema, output_dir=f"{output_base}/migrations")
            for path, content in migration_files.items():
                p = Path(project_dir) / path
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content)
                files_written.append(path)

            sg = SeedDataGenerator()
            seed_sql = sg.generate_seed_data(schema)
            seed_path = f"{output_base}/seed.sql"
            p = Path(project_dir) / seed_path
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(seed_sql)
            files_written.append(seed_path)

            og = ORMGenerator()
            orm_files = og.generate_orm_models(schema, output_dir=f"{output_base}/models")
            for path, content in orm_files.items():
                p = Path(project_dir) / path
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content)
                files_written.append(path)

            schema_json_path = f"{output_base}/schema.json"
            p = Path(project_dir) / schema_json_path
            p.write_text(self._schema_to_json(schema))
            files_written.append(schema_json_path)

        except Exception as e:
            errors.append(str(e))
            return PipelineResult(success=False, output_dir=output_base, files_written=[], errors=errors)

        return PipelineResult(success=True, output_dir=output_base, files_written=files_written, errors=errors)

    def _schema_to_json(self, schema: Schema) -> str:
        def col_to_dict(col):
            return {
                "name": col.name,
                "type": col.col_type.value,
                "nullable": col.nullable,
                "primary_key": col.primary_key,
                "unique": col.unique,
                "default": col.default,
                "references": col.references,
            }

        def table_to_dict(table):
            return {
                "name": table.name,
                "columns": [col_to_dict(c) for c in table.columns],
                "comment": table.comment,
            }

        data = {
            "tables": [table_to_dict(t) for t in schema.tables],
            "relationships": [
                {"from": r.from_table, "to": r.to_table, "type": r.relationship_type.value}
                for r in schema.relationships
            ],
            "extensions": schema.extensions,
        }
        return json.dumps(data, indent=2)


def run_from_project_spec(spec: ProjectSpec, project_dir: str = ".") -> PipelineResult:
    """Convenience function to run the full NeonDB pipeline step."""
    step = NeonDBPipelineStep()
    return step.run(project_dir=project_dir, project_spec=spec)
