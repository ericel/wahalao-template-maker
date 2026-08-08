import { useEffect, useMemo, useRef, useState } from "react";
import {
  ArrowUpRight,
  Bot,
  Check,
  ChevronRight,
  CircleAlert,
  Download,
  FileCode2,
  FolderGit2,
  Import,
  Layers3,
  Save,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import {
  initialDraft,
  recipePath,
  validateDraft,
  type TemplateDraft,
  type TemplateStatus,
} from "./lib/template";
import { createRecipeArchive, parseTemplate, serializeTemplate } from "./lib/templateYaml";

const storageKey = "wahalao-template-maker:draft:v1";

type Section = "identity" | "source" | "runtime" | "review";

function loadDraft(): TemplateDraft {
  try {
    const saved = localStorage.getItem(storageKey);
    if (!saved) return structuredClone(initialDraft);
    const parsed = JSON.parse(saved) as TemplateDraft;
    const { submission_id: _removed, ...metadata } = (parsed.metadata ??
      {}) as TemplateDraft["metadata"] & { submission_id?: string };
    return { ...parsed, metadata };
  } catch {
    return structuredClone(initialDraft);
  }
}

function downloadBlob(blob: Blob, filename: string) {
  const href = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = href;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(href);
}

function Field({
  label,
  hint,
  children,
}: {
  label: string;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <label className="field">
      <span className="field-label">{label}</span>
      {children}
      {hint ? <span className="field-hint">{hint}</span> : null}
    </label>
  );
}

function App() {
  const [draft, setDraft] = useState<TemplateDraft>(loadDraft);
  const [section, setSection] = useState<Section>("identity");
  const [savedAt, setSavedAt] = useState<string>("");
  const [notice, setNotice] = useState<string>("");
  const importRef = useRef<HTMLInputElement>(null);
  const checks = useMemo(() => validateDraft(draft), [draft]);
  const readyCount = checks.filter((check) => check.valid).length;
  const yaml = useMemo(() => serializeTemplate(draft), [draft]);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      localStorage.setItem(storageKey, JSON.stringify(draft));
      setSavedAt(new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }));
    }, 350);
    return () => window.clearTimeout(timer);
  }, [draft]);

  function updateMetadata<Key extends keyof TemplateDraft["metadata"]>(
    key: Key,
    value: TemplateDraft["metadata"][Key],
  ) {
    setDraft((current) => ({
      ...current,
      metadata: { ...current.metadata, [key]: value },
    }));
  }

  function updateSource<Key extends keyof TemplateDraft["spec"]["source"]>(
    key: Key,
    value: TemplateDraft["spec"]["source"][Key],
  ) {
    setDraft((current) => ({
      ...current,
      spec: { ...current.spec, source: { ...current.spec.source, [key]: value } },
    }));
  }

  function updateBuild<Key extends keyof TemplateDraft["spec"]["build"]>(
    key: Key,
    value: TemplateDraft["spec"]["build"][Key],
  ) {
    setDraft((current) => ({
      ...current,
      spec: { ...current.spec, build: { ...current.spec.build, [key]: value } },
    }));
  }

  async function exportRecipe() {
    const archive = await createRecipeArchive(draft);
    downloadBlob(archive, `${draft.metadata.name}-${draft.metadata.version}.zip`);
    setNotice("Recipe bundle exported with template, manifest, and README.");
  }

  async function importYaml(file: File | undefined) {
    if (!file) return;
    try {
      setDraft(parseTemplate(await file.text()));
      setNotice(`Imported ${file.name}. Review every section before export.`);
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Unable to import template YAML.");
    }
  }

  const navigation: Array<{ id: Section; label: string; icon: typeof Sparkles }> = [
    { id: "identity", label: "Identity", icon: Sparkles },
    { id: "source", label: "Source & build", icon: FolderGit2 },
    { id: "runtime", label: "Runtime", icon: Bot },
    { id: "review", label: "Review & export", icon: ShieldCheck },
  ];

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="/" aria-label="Wahalao Template Maker home">
          <span className="brand-mark"><Layers3 size={21} /></span>
          <span><strong>Wahalao</strong><small>Template Maker</small></span>
        </a>
        <div className="topbar-actions">
          <span className="autosave"><Save size={14} /> {savedAt ? `Saved ${savedAt}` : "Local draft"}</span>
          <button className="button ghost" onClick={() => importRef.current?.click()}>
            <Import size={16} /> Import YAML
          </button>
          <input
            ref={importRef}
            hidden
            type="file"
            accept=".yaml,.yml,text/yaml"
            onChange={(event) => void importYaml(event.target.files?.[0])}
          />
          <button className="button primary" onClick={() => void exportRecipe()}>
            <Download size={16} /> Export recipe
          </button>
        </div>
      </header>

      <div className="workspace">
        <aside className="sidebar">
          <div className="sidebar-kicker">Recipe workflow</div>
          <nav>
            {navigation.map((item, index) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  className={`nav-item ${section === item.id ? "active" : ""}`}
                  onClick={() => setSection(item.id)}
                >
                  <span className="nav-index">{index + 1}</span>
                  <Icon size={17} />
                  <span>{item.label}</span>
                  <ChevronRight size={15} />
                </button>
              );
            })}
          </nav>
          <div className="sidebar-card">
            <div className="sidebar-card-head"><ShieldCheck size={17} /> Registry contract</div>
            <p>Drafts export to the immutable directory expected by <code>weynear-templates</code>.</p>
            <a href="https://github.com/ericel/weynear-templates" target="_blank" rel="noreferrer">
              Open upstream <ArrowUpRight size={14} />
            </a>
          </div>
        </aside>

        <main className="editor">
          <div className="editor-heading">
            <div>
              <span className="eyebrow">{draft.metadata.publisher} / {draft.metadata.name}</span>
              <h1>{navigation.find((item) => item.id === section)?.label}</h1>
              <p>Build a reviewable, least-privilege automation recipe.</p>
            </div>
            <span className={`status-pill ${draft.metadata.status}`}>{draft.metadata.status}</span>
          </div>

          {section === "identity" ? (
            <section className="panel form-panel">
              <div className="section-title"><span>Catalog identity</span><small>Defines the immutable recipe address.</small></div>
              <div className="form-grid three">
                <Field label="Publisher"><input value={draft.metadata.publisher} onChange={(e) => updateMetadata("publisher", e.target.value.toLowerCase())} /></Field>
                <Field label="Template name"><input value={draft.metadata.name} onChange={(e) => updateMetadata("name", e.target.value.toLowerCase())} /></Field>
                <Field label="Version" hint="Strict semantic version"><input value={draft.metadata.version} onChange={(e) => updateMetadata("version", e.target.value)} /></Field>
              </div>
              <div className="form-grid two">
                <Field label="Display name"><input value={draft.metadata.display_name} onChange={(e) => updateMetadata("display_name", e.target.value)} /></Field>
                <Field label="Status">
                  <select value={draft.metadata.status} onChange={(e) => updateMetadata("status", e.target.value as TemplateStatus)}>
                    <option value="preview">Preview</option><option value="approved">Approved</option><option value="deprecated">Deprecated</option>
                  </select>
                </Field>
              </div>
              <Field label="Summary" hint={`${draft.metadata.summary.length}/300`}>
                <textarea rows={4} maxLength={300} value={draft.metadata.summary} onChange={(e) => updateMetadata("summary", e.target.value)} />
              </Field>
              <div className="form-grid two">
                <Field label="Categories" hint="Comma-separated identifiers"><input value={draft.metadata.categories.join(", ")} onChange={(e) => updateMetadata("categories", e.target.value.split(",").map((v) => v.trim()).filter(Boolean))} /></Field>
                <Field label="Tags" hint="Comma-separated identifiers"><input value={draft.metadata.tags.join(", ")} onChange={(e) => updateMetadata("tags", e.target.value.split(",").map((v) => v.trim()).filter(Boolean))} /></Field>
              </div>
            </section>
          ) : null}

          {section === "source" ? (
            <section className="panel form-panel">
              <div className="section-title"><span>Reviewed source</span><small>Pin code and declare a reproducible central build.</small></div>
              <Field label="GitHub repository"><input value={draft.spec.source.repository} onChange={(e) => updateSource("repository", e.target.value)} /></Field>
              <div className="form-grid two">
                <Field label="Full commit SHA"><input className="mono" value={draft.spec.source.commit} maxLength={40} onChange={(e) => updateSource("commit", e.target.value.toLowerCase())} /></Field>
                <Field label="Source path"><input value={draft.spec.source.path} onChange={(e) => updateSource("path", e.target.value)} /></Field>
              </div>
              <div className="form-grid two">
                <Field label="Docker build context"><input className="mono" value={draft.spec.build.context} onChange={(e) => updateBuild("context", e.target.value)} /></Field>
                <Field label="Dockerfile"><input className="mono" value={draft.spec.build.dockerfile} onChange={(e) => updateBuild("dockerfile", e.target.value)} /></Field>
              </div>
              <div className="callout"><ShieldCheck size={18} /><span>The pull request declares how to build. Weynear’s central index creates, signs, and publishes the artifact after review—no registry credentials are needed here.</span></div>
            </section>
          ) : null}

          {section === "runtime" ? (
            <section className="panel form-panel">
              <div className="section-title"><span>Installation contract</span><small>Declare what the automation needs—not who will install it.</small></div>
              <div className="form-grid two">
                <Field label="Runtime adapter"><input value={draft.spec.runtime_adapter} onChange={(e) => setDraft((current) => ({ ...current, spec: { ...current.spec, runtime_adapter: e.target.value } }))} /></Field>
                <Field label="Manifest filename"><input value={draft.spec.manifest} onChange={(e) => setDraft((current) => ({ ...current, spec: { ...current.spec, manifest: e.target.value } }))} /></Field>
              </div>
              <div className="choice-row">
                <button className={`choice ${draft.spec.bot_required ? "selected" : ""}`} onClick={() => setDraft((current) => ({ ...current, spec: { ...current.spec, bot_required: true } }))}><Bot size={19} /><span><strong>Bot required</strong><small>Installer binds a managed bot.</small></span></button>
                <button className={`choice ${!draft.spec.bot_required ? "selected" : ""}`} onClick={() => setDraft((current) => ({ ...current, spec: { ...current.spec, bot_required: false } }))}><FileCode2 size={19} /><span><strong>Headless</strong><small>No bot identity is required.</small></span></button>
              </div>
              <div className="form-grid two">
                <Field label="Moderation content kind"><input value={draft.spec.moderation.content_kind} onChange={(e) => setDraft((current) => ({ ...current, spec: { ...current.spec, moderation: { ...current.spec.moderation, content_kind: e.target.value } } }))} /></Field>
                <Field label="Compatible environments">
                  <select value={draft.spec.compatibility.environments.join(",")} onChange={(e) => setDraft((current) => ({ ...current, spec: { ...current.spec, compatibility: { ...current.spec.compatibility, environments: e.target.value.split(",") as Array<"test" | "live"> } } }))}>
                    <option value="test">Test only</option><option value="test,live">Test and live</option><option value="live">Live only</option>
                  </select>
                </Field>
              </div>
              <div className="callout"><ShieldCheck size={18} /><span>Credentials, user IDs, bot IDs, recipient lists, and application IDs never belong in a public recipe.</span></div>
            </section>
          ) : null}

          {section === "review" ? (
            <section className="review-grid">
              <div className="panel checks-panel">
                <div className="section-title"><span>Preflight</span><small>{readyCount} of {checks.length} checks passing.</small></div>
                <div className="progress"><span style={{ width: `${(readyCount / checks.length) * 100}%` }} /></div>
                <div className="checks">
                  {checks.map((check) => (
                    <div className="check" key={check.id}>
                      <span className={check.valid ? "check-icon valid" : "check-icon"}>{check.valid ? <Check size={15} /> : <CircleAlert size={15} />}</span>
                      <span><strong>{check.label}</strong><small>{check.detail}</small></span>
                    </div>
                  ))}
                </div>
                <div className="export-path"><small>Export destination</small><code>{recipePath(draft)}/</code></div>
                <button className="button primary wide" onClick={() => void exportRecipe()}><Download size={17} /> Export pull-request bundle</button>
              </div>
              <div className="panel yaml-panel">
                <div className="code-heading"><span><FileCode2 size={16} /> template.yaml</span><small>Generated preview</small></div>
                <pre>{yaml}</pre>
              </div>
            </section>
          ) : null}

          {notice ? <button className="toast" onClick={() => setNotice("")}>{notice}<span>Dismiss</span></button> : null}
        </main>
      </div>
    </div>
  );
}

export default App;
