# Wahalao Template Maker

A local authoring workbench for building automation recipe bundles before proposing them to [`weynear-templates`](https://github.com/ericel/weynear-templates).

This repository owns multiple source templates and their reproducible build
definitions, including live sports scores and RSS/Atom news publishing.

## What the scaffold provides

- guided metadata, source, reproducible build, runtime, and moderation fields;
- automatic browser-local draft persistence;
- YAML import and generated `template.yaml` preview;
- lightweight preflight checks aligned with the upstream v1 schema;
- ZIP export using the upstream path:
  `registry/recipes/<publisher>/<template>/<version>/`;
- generated `template.yaml`, `manifest.yaml`, and `README.md` starter files.

This app intentionally does not store secrets, credentials, user IDs, bot IDs, recipient lists, or application IDs.

## Contribution workflow

1. Author the recipe in Template Maker and commit the template source.
2. Export the recipe and open a pull request against `weynear-templates`.
3. After review, central build, signing, and publication, the template appears
   in the Automations catalog and any eligible application can install it.

Recipes carry no submission ID and no installation secret. Publisher ownership
comes from the reviewed publisher record in `weynear-templates` and the source
repositories registered against it. A recipe still carrying a legacy
`metadata.submission_id` is rejected at export and by registry CI.

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

## Owned templates

```text
templates/sports-live-scores/
  src/sports_live_scores/       capability-bound source
  tests/                        source contract tests
  recipe/2.2.0/                 next immutable registry candidate
  Dockerfile                    OCI artifact definition
templates/news-feed-publisher/
  src/news_feed_publisher/      canonical-link publishing source
  tests/                        source contract tests
  recipe/1.1.0/                 public-HTTPS feed registry candidate
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

After pushing the source commit, submit the recipe with one command:

```bash
npm run submit:sports
npm run submit:news
```

The command verifies that the source commit is pushed, prepares the immutable
recipe, creates a clean `weynear-templates` branch, validates it, pushes it, and
opens the pull request using the developer's existing `gh` login. It stores no
GitHub, Artifact Registry, KMS, or index credentials in this repository.

The browser preflight is an authoring aid; the upstream JSON Schema and CI remain authoritative.
