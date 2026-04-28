"""CLI tool for the NeonDB schema designer.

Usage:
    python -m neon_db_designer.cli --name "TaskApp" \\
        --description "A task management application" \\
        --features "user accounts" "project management" \\
        --output-dir "." \\
        --models '[{"name": "tasks", "columns": [{"name": "title", "type": "VARCHAR"}]}]'
"""
from __future__ import annotations

import argparse
import json
import sys

from neon_db_designer.models import ProjectSpec
from neon_db_designer.pipeline import NeonDBPipelineStep, run_from_project_spec


def main() -> None:
    parser = argparse.ArgumentParser(description="NeonDB schema designer and migration generator")
    parser.add_argument("--name", required=True, help="Project name")
    parser.add_argument("--description", required=True, help="Project description")
    parser.add_argument(
        "--features",
        nargs="*",
        default=[],
        help="Feature keywords (used to infer schema needs)",
    )
    parser.add_argument(
        "--models",
        default="[]",
        help="JSON array of model definitions",
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory to write generated files",
    )
    parser.add_argument(
        "--tech-stack",
        default="{}",
        help="JSON dict of tech stack preferences",
    )
    parser.add_argument(
        "--print-schema",
        action="store_true",
        help="Print the generated schema JSON to stdout",
    )

    args = parser.parse_args()

    try:
        models = json.loads(args.models)
    except json.JSONDecodeError as e:
        print(f"Error: --models must be valid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        tech_stack = json.loads(args.tech_stack)
    except json.JSONDecodeError as e:
        print(f"Error: --tech-stack must be valid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    spec = ProjectSpec(
        name=args.name,
        description=args.description,
        features=args.features,
        models=models,
        tech_stack=tech_stack,
    )

    if args.print_schema:
        from neon_db_designer.schemas.schema_designer import SchemaDesigner
        designer = SchemaDesigner()
        schema = designer.generate_schema(spec)
        from neon_db_designer.pipeline import NeonDBPipelineStep
        step = NeonDBPipelineStep()
        print(step._schema_to_json(schema))
        sys.exit(0)

    result = run_from_project_spec(spec, project_dir=args.output_dir)

    if not result.success:
        print("Errors encountered:", file=sys.stderr)
        for err in result.errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(1)

    print(f"Successfully generated {len(result.files_written)} files in {result.output_dir}/:")
    for f in result.files_written:
        print(f"  {f}")


if __name__ == "__main__":
    main()
