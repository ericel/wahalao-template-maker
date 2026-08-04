#!/usr/bin/env bash
set -euo pipefail

SOURCE_REPOSITORY="ericel/wahalao-template-maker"
INDEX_REPOSITORY="ericel/weynear-templates"
TEMPLATE_NAME="${1:-}"
REQUESTED_VERSION="${2:-}"

if [[ -z "$TEMPLATE_NAME" ]]; then
  echo "Usage: npm run submit -- <template-name> [version]" >&2
  exit 1
fi

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_COMMIT="$(git -C "$PROJECT_ROOT" rev-parse HEAD)"
SOURCE_BRANCH="$(git -C "$PROJECT_ROOT" branch --show-current)"

for command_name in git gh; do
  command -v "$command_name" >/dev/null 2>&1 || {
    echo "Required command is not installed: $command_name" >&2
    exit 1
  }
done

if [[ -z "$SOURCE_BRANCH" ]]; then
  echo "Submit from a named source branch, not a detached HEAD." >&2
  exit 1
fi

gh auth status >/dev/null
REMOTE_COMMIT="$(gh api "repos/${SOURCE_REPOSITORY}/commits/${SOURCE_BRANCH}" --jq '.sha')"
if [[ "$REMOTE_COMMIT" != "$SOURCE_COMMIT" ]]; then
  echo "Push the current commit before submitting it to Weynear Templates." >&2
  echo "Local:  $SOURCE_COMMIT" >&2
  echo "Remote: ${REMOTE_COMMIT:-missing}" >&2
  exit 1
fi

TASK_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/wahalao-template-submit.XXXXXX")"
cleanup() { rm -rf "$TASK_ROOT"; }
trap cleanup EXIT
EXPORT_ROOT="$TASK_ROOT/contribution"
INDEX_ROOT="$TASK_ROOT/weynear-templates"
INDEX_VENV="$TASK_ROOT/index-venv"
TEMPLATE_PYTHON="python3"
if [[ -x "$PROJECT_ROOT/.venv/bin/python" ]]; then
  TEMPLATE_PYTHON="$PROJECT_ROOT/.venv/bin/python"
fi

PREPARE_ARGS=(
  --template-name "$TEMPLATE_NAME"
  --source-commit "$SOURCE_COMMIT"
  --destination-root "$EXPORT_ROOT"
)
if [[ -n "$REQUESTED_VERSION" ]]; then
  PREPARE_ARGS+=(--version "$REQUESTED_VERSION")
fi
OUTPUT_PATH="$("$TEMPLATE_PYTHON" "$PROJECT_ROOT/scripts/prepare_contribution.py" "${PREPARE_ARGS[@]}")"
TEMPLATE_VERSION="$(basename "$OUTPUT_PATH")"
SUBMISSION_BRANCH="submit/${TEMPLATE_NAME}-${TEMPLATE_VERSION}"

echo "Preparing ${TEMPLATE_NAME}@${TEMPLATE_VERSION} from ${SOURCE_COMMIT}..."
echo "Creating a clean Weynear Templates contribution branch..."
git -c credential.helper='!gh auth git-credential' clone --quiet \
  "https://github.com/${INDEX_REPOSITORY}.git" "$INDEX_ROOT"
git -C "$INDEX_ROOT" switch -c "$SUBMISSION_BRANCH" origin/main
rsync -a "$EXPORT_ROOT/registry/" "$INDEX_ROOT/registry/"
if ! grep -q '"placeholder"' "$INDEX_ROOT/schemas/template.schema.json"; then
  git -C "$INDEX_ROOT" apply \
    "$PROJECT_ROOT/patches/weynear-templates/configuration-ui-metadata.patch"
fi

echo "Installing the Weynear Templates validation toolchain..."
"$TEMPLATE_PYTHON" -m venv "$INDEX_VENV"
"$INDEX_VENV/bin/python" -m pip install --quiet --disable-pip-version-check \
  -r "$INDEX_ROOT/requirements-dev.txt"
echo "Validating the upstream index contribution..."
"$INDEX_VENV/bin/python" "$INDEX_ROOT/scripts/build_catalog.py" --check
(
  cd "$INDEX_ROOT"
  "$INDEX_VENV/bin/python" -m pytest -q
)

if [[ "${WAHALAO_SUBMIT_DRY_RUN:-0}" == "1" ]]; then
  echo "Submission preflight completed successfully."
  exit 0
fi

git -C "$INDEX_ROOT" add \
  "registry/recipes/weynear/${TEMPLATE_NAME}/${TEMPLATE_VERSION}" \
  "schemas/template.schema.json"
git -C "$INDEX_ROOT" commit -m "Submit ${TEMPLATE_NAME} ${TEMPLATE_VERSION}"
git -C "$INDEX_ROOT" -c credential.helper='!gh auth git-credential' \
  push -u origin "$SUBMISSION_BRANCH"

PR_URL="$(gh pr create \
  --repo "$INDEX_REPOSITORY" \
  --base main \
  --head "$SUBMISSION_BRANCH" \
  --title "Submit ${TEMPLATE_NAME} ${TEMPLATE_VERSION}" \
  --body "Private app-owned template submission for \`weynear/${TEMPLATE_NAME}@${TEMPLATE_VERSION}\` from \`https://github.com/${SOURCE_REPOSITORY}@${SOURCE_COMMIT}\`. The source contains no credentials or tenant identifiers and passed the upstream catalog and adversarial tests.")"

echo
echo "Submitted successfully: $PR_URL"
