#!/usr/bin/env python3
"""Export any owned template recipe without registry credentials."""

import argparse
import re
import shutil
from pathlib import Path

import yaml


COMMIT_PATTERN = re.compile(r"^[a-f0-9]{40}$")
IDENTIFIER_PATTERN = re.compile(r"^[a-z][a-z0-9-]{1,62}$")
SEMVER_PATTERN = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")


def _latest_version(recipe_root: Path) -> str:
    versions = [
        (tuple(int(part) for part in item.name.split(".")), item.name)
        for item in recipe_root.iterdir()
        if item.is_dir() and SEMVER_PATTERN.fullmatch(item.name)
    ]
    if not versions:
        raise ValueError(f"no semantic versions found in {recipe_root}")
    return max(versions)[1]


def prepare_contribution(
    template_name: str,
    source_commit: str,
    destination_root: Path,
    *,
    version: str | None = None,
) -> Path:
    if not IDENTIFIER_PATTERN.fullmatch(template_name):
        raise ValueError("template_name must be a registry identifier")
    if not COMMIT_PATTERN.fullmatch(source_commit) or source_commit == "0" * 40:
        raise ValueError("source_commit must be a non-placeholder lowercase Git SHA")
    project_root = Path(__file__).resolve().parents[1]
    recipe_root = project_root / "templates" / template_name / "recipe"
    selected_version = version or _latest_version(recipe_root)
    if not SEMVER_PATTERN.fullmatch(selected_version):
        raise ValueError("version must be strict semantic versioning")
    candidate = recipe_root / selected_version
    if not candidate.is_dir():
        raise ValueError(f"recipe does not exist: {template_name}@{selected_version}")
    output = (
        destination_root
        / "registry"
        / "recipes"
        / "weynear"
        / template_name
        / selected_version
    )
    if output.exists():
        raise FileExistsError(f"immutable recipe already exists: {output}")
    shutil.copytree(candidate, output)
    template_path = output / "template.yaml"
    template = yaml.safe_load(template_path.read_text(encoding="utf-8"))
    metadata = template.setdefault("metadata", {})
    if metadata.get("name") != template_name or metadata.get("version") != selected_version:
        raise ValueError("recipe metadata does not match its source path")
    if "submission_id" in metadata:
        raise ValueError("recipes must not carry metadata.submission_id")
    template["spec"]["source"]["commit"] = source_commit
    if "artifact" in template["spec"]:
        raise ValueError("contributor recipes must not declare trusted artifacts")
    template_path.write_text(
        yaml.safe_dump(template, sort_keys=False),
        encoding="utf-8",
    )
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template-name", required=True)
    parser.add_argument("--version")
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--destination-root", type=Path, required=True)
    args = parser.parse_args()
    print(prepare_contribution(
        args.template_name,
        args.source_commit,
        args.destination_root,
        version=args.version,
    ))


if __name__ == "__main__":
    main()
