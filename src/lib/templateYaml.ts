import yaml from "js-yaml";
import JSZip from "jszip";
import { recipePath, type TemplateDraft } from "./template";

export function serializeTemplate(draft: TemplateDraft): string {
  return yaml.dump(draft, { noRefs: true, lineWidth: 100, sortKeys: false });
}

export function parseTemplate(source: string): TemplateDraft {
  const parsed = yaml.load(source);
  if (!parsed || typeof parsed !== "object") {
    throw new Error("Template YAML must contain an object.");
  }
  const draft = parsed as TemplateDraft;
  const { submission_id: _removed, ...metadata } = (draft.metadata ??
    {}) as TemplateDraft["metadata"] & { submission_id?: string };
  return { ...draft, metadata };
}

export function createManifest(draft: TemplateDraft): string {
  return yaml.dump(
    {
      api_version: "automations.weynear.com/v1",
      kind: "AutomationInstallManifest",
      metadata: { template: `${draft.metadata.publisher}/${draft.metadata.name}@${draft.metadata.version}` },
      spec: { configuration: {}, bindings: {} },
    },
    { noRefs: true, lineWidth: 100 },
  );
}

export function createReadme(draft: TemplateDraft): string {
  return `# ${draft.metadata.display_name}\n\n${draft.metadata.summary}\n\n## Runtime\n\n- Adapter: \`${draft.spec.runtime_adapter}\`\n- Runtime: \`${draft.spec.compatibility.runtime}\`\n- Bot required: ${draft.spec.bot_required ? "yes" : "no"}\n\n## Review notes\n\nDescribe setup, fixtures, expected output, moderation behavior, and rollback here.\n`;
}

export async function createRecipeArchive(draft: TemplateDraft): Promise<Blob> {
  const zip = new JSZip();
  const folder = zip.folder(recipePath(draft));
  if (!folder) {
    throw new Error("Unable to create recipe folder.");
  }
  folder.file("template.yaml", serializeTemplate(draft));
  folder.file(draft.spec.manifest, createManifest(draft));
  folder.file("README.md", createReadme(draft));
  return zip.generateAsync({ type: "blob" });
}
