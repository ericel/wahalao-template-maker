# Wahalao Template Maker

A local authoring workbench for building automation recipe bundles before proposing them to [`weynear-templates`](https://github.com/ericel/weynear-templates).

## What the scaffold provides

- guided metadata, source, artifact, runtime, and moderation fields;
- automatic browser-local draft persistence;
- YAML import and generated `template.yaml` preview;
- lightweight preflight checks aligned with the upstream v1 schema;
- ZIP export using the upstream path:
  `registry/recipes/<publisher>/<template>/<version>/`;
- generated `template.yaml`, `manifest.yaml`, and `README.md` starter files.

This app intentionally does not store secrets, credentials, user IDs, bot IDs, recipient lists, or application IDs.

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
```

After exporting a recipe, unpack it into a clean branch of `weynear-templates`, replace placeholder source/artifact hashes, and run the upstream validation:

```bash
cd /Users/ojobasi/dev/weynear-templates
.venv/bin/python scripts/build_catalog.py --check
.venv/bin/python -m pytest -q
```

The browser preflight is an authoring aid; the upstream JSON Schema and CI remain authoritative.
