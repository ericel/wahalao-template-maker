# Wahalao Template Maker

A local authoring workbench for building automation recipe bundles before proposing them to [`weynear-templates`](https://github.com/ericel/weynear-templates).

This repository also owns the source and reproducible build definition for the next
`weynear/sports-live-scores` release. Approved `1.x` releases remain immutable
and continue to point to `wahalao-automation`; the first app-scoped release is `2.1.0`.

## What the scaffold provides

- guided metadata, source, reproducible build, runtime, and moderation fields;
- automatic browser-local draft persistence;
- YAML import and generated `template.yaml` preview;
- lightweight preflight checks aligned with the upstream v1 schema;
- ZIP export using the upstream path:
  `registry/recipes/<publisher>/<template>/<version>/`;
- generated `template.yaml`, `manifest.yaml`, and `README.md` starter files.

This app intentionally does not store secrets, credentials, user IDs, bot IDs, recipient lists, or application IDs.

## Private submission workflow

1. Open `/developer/messaging#automations`, select the owning application, and
   create a private template submission.
2. Copy the opaque `atsub_...` identifier into Template Maker. It contains no
   credentials or tenant IDs; Automation retains the authoritative app binding.
3. Export the recipe and open a pull request against `weynear-templates`.
4. After review, central build, signing, and publication, the template appears
   only in the owning application's Automations catalog.

Every version requires a new submission. Do not reuse a submission across
applications or template versions.

## Run locally

```bash
npm install
npm run dev
```

Then open the URL printed by Vite, normally `http://localhost:5173`.

## Verify

```bash
npm test
npm run build
.venv/bin/python -m pytest
```

## Owned sports template

```text
templates/sports-live-scores/
  src/sports_live_scores/       capability-bound source
  tests/                        source contract tests
  recipe/2.1.0/                 next immutable registry candidate
  Dockerfile                    OCI artifact definition
.github/workflows/
  validate.yml                         app and source validation
  export-sports-contribution.yml       credential-free, submission-bound recipe export
```

This repository needs no Weynear credentials. Its export workflow pins the
public source commit, verifies that the Docker build succeeds, and produces a
normal contribution bundle. `weynear-templates` owns the privileged build,
Artifact Registry publication, SBOM, provenance, KMS signing, and promotion.

The current `sports-live-scores-v1` runtime adapter remains in
`wahalao-automation`. That is platform runtime compatibility, not template
source ownership; it can continue loading the new signed artifact without
rewriting approved historical recipes.

Run the export workflow with the owning app's opaque `atsub_...` identifier.
After exporting the resulting recipe, unpack it into a clean branch of `weynear-templates`
and run the upstream validation. The contribution intentionally has no artifact
digest; the central index supplies it after review:

```bash
cd /Users/ojobasi/dev/weynear-templates
.venv/bin/python scripts/build_catalog.py --check
.venv/bin/python -m pytest -q
```

The browser preflight is an authoring aid; the upstream JSON Schema and CI remain authoritative.
