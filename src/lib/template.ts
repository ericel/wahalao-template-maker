export type TemplateStatus = "preview" | "approved" | "deprecated";

export type TemplateDraft = {
  api_version: "registry.automations.weynear.com/v1";
  kind: "AutomationTemplate";
  metadata: {
    publisher: string;
    name: string;
    version: string;
    display_name: string;
    summary: string;
    status: TemplateStatus;
    license: string;
    categories: string[];
    tags: string[];
  };
  spec: {
    source: {
      repository: string;
      commit: string;
      path: string;
    };
    build: {
      context: string;
      dockerfile: string;
      platform: { os: "linux"; architecture: "amd64" };
    };
    artifact?: {
      uri: string;
      digest: string;
      media_type: "application/vnd.oci.image.manifest.v1+json";
      platform: { os: "linux"; architecture: "amd64" };
    };
    runtime_adapter: string;
    bot_required: boolean;
    configuration: Array<{
      key: string;
      type: "string" | "integer" | "boolean" | "url";
      required: boolean;
      secret: boolean;
      description: string;
    }>;
    bindings: Array<Record<string, unknown>>;
    compatibility: {
      environments: Array<"test" | "live">;
      runtime: "python3.12";
    };
    moderation: {
      content_kind: string;
      sources_required: boolean;
    };
    manifest: string;
  };
};

export type ValidationItem = {
  id: string;
  label: string;
  detail: string;
  valid: boolean;
};

const identifierPattern = /^[a-z][a-z0-9-]{1,62}$/;
const semverPattern = /^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$/;
const commitPattern = /^[a-f0-9]{40}$/;
const repositoryPattern = /^https:\/\/github\.com\/[a-z0-9_.-]+\/[a-z0-9_.-]+$/;

export const initialDraft: TemplateDraft = {
  api_version: "registry.automations.weynear.com/v1",
  kind: "AutomationTemplate",
  metadata: {
    publisher: "weynear",
    name: "new-template",
    version: "0.1.0",
    display_name: "New automation",
    summary: "Describe the user outcome this automation provides.",
    status: "preview",
    license: "Apache-2.0",
    categories: ["productivity"],
    tags: ["starter"],
  },
  spec: {
    source: {
      repository: "https://github.com/ericel/wahalao-template-maker",
      commit: "0".repeat(40),
      path: "templates/new-template",
    },
    build: {
      context: "templates/new-template",
      dockerfile: "templates/new-template/Dockerfile",
      platform: { os: "linux", architecture: "amd64" },
    },
    runtime_adapter: "weynear-python-v1",
    bot_required: true,
    configuration: [],
    bindings: [],
    compatibility: {
      environments: ["test"],
      runtime: "python3.12",
    },
    moderation: {
      content_kind: "general",
      sources_required: false,
    },
    manifest: "manifest.yaml",
  },
};

export function validateDraft(draft: TemplateDraft): ValidationItem[] {
  return [
    {
      id: "identity",
      label: "Registry identity",
      detail: "Publisher and name use Weynear identifiers.",
      valid: identifierPattern.test(draft.metadata.publisher) && identifierPattern.test(draft.metadata.name),
    },
    {
      id: "version",
      label: "Immutable version",
      detail: "Version is strict semantic versioning.",
      valid: semverPattern.test(draft.metadata.version),
    },
    {
      id: "copy",
      label: "Catalog copy",
      detail: "Display name and summary are within schema limits.",
      valid: draft.metadata.display_name.trim().length > 0
        && draft.metadata.display_name.length <= 100
        && draft.metadata.summary.trim().length > 0
        && draft.metadata.summary.length <= 300,
    },
    {
      id: "source",
      label: "Reviewable source",
      detail: "Repository is GitHub and revision is a full commit SHA.",
      valid: repositoryPattern.test(draft.spec.source.repository)
        && commitPattern.test(draft.spec.source.commit)
        && draft.spec.source.commit !== "0".repeat(40),
    },
    {
      id: "build",
      label: "Reproducible build",
      detail: "The central index receives a repository-relative Docker build definition.",
      valid: Boolean(draft.spec.build.context.trim())
        && Boolean(draft.spec.build.dockerfile.trim())
        && !draft.spec.build.context.startsWith("/")
        && !draft.spec.build.dockerfile.startsWith("/")
        && !draft.spec.build.context.split("/").includes("..")
        && !draft.spec.build.dockerfile.split("/").includes(".."),
    },
    {
      id: "runtime",
      label: "Supported runtime",
      detail: "The initial registry contract requires Python 3.12.",
      valid: draft.spec.compatibility.runtime === "python3.12"
        && draft.spec.compatibility.environments.length > 0,
    },
  ];
}

export function recipePath(draft: TemplateDraft): string {
  return `registry/recipes/${draft.metadata.publisher}/${draft.metadata.name}/${draft.metadata.version}`;
}
