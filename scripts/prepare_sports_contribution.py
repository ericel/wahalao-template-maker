#!/usr/bin/env python3
"""Export the sports source recipe without any registry credentials."""

import argparse
import re
import shutil
from pathlib import Path

import yaml


REPOSITORY = "https://github.com/ericel/wahalao-template-maker"
COMMIT_PATTERN = re.compile(r"^[a-f0-9]{40}$")
VERSION = "2.2.0"


def prepare_contribution(
    source_commit: str,
    destination_root: Path,
) -> Path:
    if not COMMIT_PATTERN.fullmatch(source_commit):
        raise ValueError("source_commit must be a full lowercase Git commit SHA")
    if source_commit == "0" * 40:
        raise ValueError("source_commit cannot be the placeholder SHA")
    project_root = Path(__file__).resolve().parents[1]
    candidate = project_root / f"templates/sports-live-scores/recipe/{VERSION}"

    output = destination_root / f"registry/recipes/weynear/sports-live-scores/{VERSION}"
    if output.exists():
        raise FileExistsError(f"immutable recipe already exists: {output}")
    shutil.copytree(candidate, output)

    template_path = output / "template.yaml"
    template = yaml.safe_load(template_path.read_text())
    if "submission_id" in template.get("metadata", {}):
        raise ValueError("recipes must not carry metadata.submission_id")
    template["spec"]["source"]["commit"] = source_commit
    if "artifact" in template["spec"]:
        raise ValueError("contributor recipes must not declare trusted artifacts")
    template_path.write_text(yaml.safe_dump(template, sort_keys=False), encoding="utf-8")
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--destination-root", type=Path, required=True)
    args = parser.parse_args()
    print(prepare_contribution(args.source_commit, args.destination_root))


if __name__ == "__main__":
    main()
