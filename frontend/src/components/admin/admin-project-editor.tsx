"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import {
  type AdminProject,
  type AdminProjectFormOptions,
  type ProjectBlockWrite,
  type ProjectWrite,
  createAdminProject,
  getAdminProject,
  getAdminProjectFormOptions,
  replaceAdminProjectBlocks,
  updateAdminProject,
} from "@/lib/admin-api";

import { useAdminSession } from "./admin-session-provider";

type ProjectFormState = {
  architect_en: string;
  architect_fa: string;
  area_en: string;
  area_fa: string;
  client_en: string;
  client_fa: string;
  collaborators_en: string;
  collaborators_fa: string;
  completion_date: string;
  completion_year: string;
  discipline_ids: string[];
  featured: boolean;
  intro_en: string;
  intro_fa: string;
  intro_title_en: string;
  intro_title_fa: string;
  location_en: string;
  location_fa: string;
  material_en: string;
  material_fa: string;
  material_title_en: string;
  material_title_fa: string;
  narrative_en: string;
  narrative_fa: string;
  narrative_title_en: string;
  narrative_title_fa: string;
  publication_state: "draft" | "published";
  published_at: string;
  quote_en: string;
  quote_fa: string;
  scope_en: string;
  scope_fa: string;
  seo_description_en: string;
  seo_description_fa: string;
  seo_title_en: string;
  seo_title_fa: string;
  slug: string;
  status_en: string;
  status_fa: string;
  subtitle_en: string;
  subtitle_fa: string;
  summary_en: string;
  summary_fa: string;
  title_en: string;
  title_fa: string;
  typology_ids: string[];
};

type TextFieldName = Exclude<
  keyof ProjectFormState,
  "discipline_ids" | "featured" | "publication_state" | "typology_ids"
>;

const tabs = ["General", "Content", "Details", "Gallery", "SEO", "Publishing"] as const;
type Tab = (typeof tabs)[number];

const blankForm: ProjectFormState = {
  architect_en: "",
  architect_fa: "",
  area_en: "",
  area_fa: "",
  client_en: "",
  client_fa: "",
  collaborators_en: "",
  collaborators_fa: "",
  completion_date: "",
  completion_year: "",
  discipline_ids: [],
  featured: false,
  intro_en: "",
  intro_fa: "",
  intro_title_en: "",
  intro_title_fa: "",
  location_en: "",
  location_fa: "",
  material_en: "",
  material_fa: "",
  material_title_en: "",
  material_title_fa: "",
  narrative_en: "",
  narrative_fa: "",
  narrative_title_en: "",
  narrative_title_fa: "",
  publication_state: "draft",
  published_at: "",
  quote_en: "",
  quote_fa: "",
  scope_en: "",
  scope_fa: "",
  seo_description_en: "",
  seo_description_fa: "",
  seo_title_en: "",
  seo_title_fa: "",
  slug: "",
  status_en: "",
  status_fa: "",
  subtitle_en: "",
  subtitle_fa: "",
  summary_en: "",
  summary_fa: "",
  title_en: "",
  title_fa: "",
  typology_ids: [],
};

function asForm(project: AdminProject): ProjectFormState {
  return {
    architect_en: project.architect_en ?? "",
    architect_fa: project.architect_fa ?? "",
    area_en: project.area_en ?? "",
    area_fa: project.area_fa ?? "",
    client_en: project.client_en ?? "",
    client_fa: project.client_fa ?? "",
    collaborators_en: project.collaborators_en ?? "",
    collaborators_fa: project.collaborators_fa ?? "",
    completion_date: project.completion_date ?? "",
    completion_year: project.completion_year?.toString() ?? "",
    discipline_ids: project.disciplines.map((item) => item.id),
    featured: project.featured,
    intro_en: project.intro_en ?? "",
    intro_fa: project.intro_fa ?? "",
    intro_title_en: project.intro_title_en ?? "",
    intro_title_fa: project.intro_title_fa ?? "",
    location_en: project.location_en,
    location_fa: project.location_fa,
    material_en: project.material_en ?? "",
    material_fa: project.material_fa ?? "",
    material_title_en: project.material_title_en ?? "",
    material_title_fa: project.material_title_fa ?? "",
    narrative_en: project.narrative_en ?? "",
    narrative_fa: project.narrative_fa ?? "",
    narrative_title_en: project.narrative_title_en ?? "",
    narrative_title_fa: project.narrative_title_fa ?? "",
    publication_state: project.publication_state,
    published_at: project.published_at?.slice(0, 16) ?? "",
    quote_en: project.quote_en ?? "",
    quote_fa: project.quote_fa ?? "",
    scope_en: project.scope_en ?? "",
    scope_fa: project.scope_fa ?? "",
    seo_description_en: project.seo_description_en ?? "",
    seo_description_fa: project.seo_description_fa ?? "",
    seo_title_en: project.seo_title_en ?? "",
    seo_title_fa: project.seo_title_fa ?? "",
    slug: project.slug,
    status_en: project.status_en ?? "",
    status_fa: project.status_fa ?? "",
    subtitle_en: project.subtitle_en ?? "",
    subtitle_fa: project.subtitle_fa ?? "",
    summary_en: project.summary_en,
    summary_fa: project.summary_fa,
    title_en: project.title_en,
    title_fa: project.title_fa,
    typology_ids: project.typologies.map((item) => item.id),
  };
}

function asProjectWrite(form: ProjectFormState): ProjectWrite {
  const { slug, ...rest } = form;
  void slug;
  return {
    ...rest,
    completion_date: form.completion_date || null,
    completion_year: form.completion_year ? Number(form.completion_year) : null,
    published_at: form.published_at || null,
  };
}

function asBlockWrite(block: AdminProject["blocks"][number]): ProjectBlockWrite {
  return {
    block_type: block.block_type,
    content_en: block.content_en,
    content_fa: block.content_fa,
  } as ProjectBlockWrite;
}

function TextField({
  label,
  multiline = false,
  onChange,
  required = false,
  value,
}: {
  label: string;
  multiline?: boolean;
  onChange: (value: string) => void;
  required?: boolean;
  value: string;
}) {
  return (
    <label className="admin-editor__field">
      <span>{label}</span>
      {multiline ? (
        <textarea onChange={(event) => onChange(event.target.value)} required={required} rows={5} value={value} />
      ) : (
        <input onChange={(event) => onChange(event.target.value)} required={required} value={value} />
      )}
    </label>
  );
}

function TaxonomyChecklist({
  label,
  onChange,
  options,
  selected,
}: {
  label: string;
  onChange: (identifiers: string[]) => void;
  options: AdminProjectFormOptions["disciplines"];
  selected: string[];
}) {
  return (
    <fieldset className="admin-editor__checklist">
      <legend>{label}</legend>
      {options.map((item) => {
        const checked = selected.includes(item.id);
        return (
          <label key={item.id}>
            <input
              checked={checked}
              onChange={() =>
                onChange(checked ? selected.filter((id) => id !== item.id) : [...selected, item.id])
              }
              type="checkbox"
            />
            <span>{item.title_en}</span>
            <span dir="rtl">{item.title_fa}</span>
          </label>
        );
      })}
    </fieldset>
  );
}

function ProjectBlocksEditor({
  blocks,
  disabled,
  onChange,
}: {
  blocks: ProjectBlockWrite[];
  disabled: boolean;
  onChange: (blocks: ProjectBlockWrite[]) => void;
}) {
  const update = (index: number, nextBlock: ProjectBlockWrite) => {
    onChange(blocks.map((block, current) => (current === index ? nextBlock : block)));
  };

  return (
    <div className="admin-block-editor">
      <p>Text and quote blocks are rendered publicly now. Image blocks require managed media and become editable in the media phase.</p>
      {blocks.map((block, index) => (
        <article className="admin-block-editor__block" key={`${block.block_type}-${index}`}>
          {block.block_type === "text" ? (
            <>
              <TextField
                label="Text heading / EN"
                onChange={(heading) => update(index, { ...block, content_en: { ...block.content_en, heading } })}
                value={block.content_en.heading ?? ""}
              />
              <TextField
                label="Text body / EN"
                multiline
                onChange={(body) => update(index, { ...block, content_en: { ...block.content_en, body } })}
                value={block.content_en.body}
              />
              <TextField
                label="Text heading / FA"
                onChange={(heading) => update(index, { ...block, content_fa: { ...block.content_fa, heading } })}
                value={block.content_fa.heading ?? ""}
              />
              <TextField
                label="Text body / FA"
                multiline
                onChange={(body) => update(index, { ...block, content_fa: { ...block.content_fa, body } })}
                value={block.content_fa.body}
              />
            </>
          ) : block.block_type === "quote" ? (
            <>
              <TextField
                label="Quote / EN"
                multiline
                onChange={(quote) => update(index, { ...block, content_en: { ...block.content_en, quote } })}
                value={block.content_en.quote}
              />
              <TextField
                label="Quote / FA"
                multiline
                onChange={(quote) => update(index, { ...block, content_fa: { ...block.content_fa, quote } })}
                value={block.content_fa.quote}
              />
            </>
          ) : (
            <p>Managed media block: {block.block_type}</p>
          )}
          <button disabled={disabled} onClick={() => onChange(blocks.filter((_, current) => current !== index))} type="button">
            Remove block
          </button>
        </article>
      ))}
      <div className="admin-projects__toolbar">
        <button
          disabled={disabled}
          onClick={() =>
            onChange([
              ...blocks,
              { block_type: "text", content_en: { body: "" }, content_fa: { body: "" } },
            ])
          }
          type="button"
        >
          Add text block
        </button>
        <button
          disabled={disabled}
          onClick={() =>
            onChange([
              ...blocks,
              { block_type: "quote", content_en: { quote: "" }, content_fa: { quote: "" } },
            ])
          }
          type="button"
        >
          Add quote block
        </button>
      </div>
    </div>
  );
}

export function AdminProjectEditor({ projectId }: { projectId?: string }) {
  const { session } = useAdminSession();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<Tab>("General");
  const [blocks, setBlocks] = useState<ProjectBlockWrite[]>([]);
  const [form, setForm] = useState<ProjectFormState>(blankForm);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [options, setOptions] = useState<AdminProjectFormOptions | null>(null);
  const [project, setProject] = useState<AdminProject | null>(null);

  useEffect(() => {
    let active = true;
    async function loadEditor() {
      try {
        const [nextOptions, nextProject] = await Promise.all([
          getAdminProjectFormOptions(),
          projectId === undefined ? Promise.resolve(null) : getAdminProject(projectId),
        ]);
        if (!active) return;
        setOptions(nextOptions);
        if (nextProject !== null) {
          setProject(nextProject);
          setForm(asForm(nextProject));
          setBlocks(nextProject.blocks.map(asBlockWrite));
        }
      } catch {
        if (active) setMessage("The project editor is unavailable. Refresh to try again.");
      } finally {
        if (active) setIsLoading(false);
      }
    }
    void loadEditor();
    return () => {
      active = false;
    };
  }, [projectId]);

  const setText = (field: TextFieldName, value: string) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const saveProject = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (session === null) return;
    setIsSaving(true);
    setMessage(null);
    try {
      const payload = asProjectWrite(form);
      const saved =
        project === null
          ? await createAdminProject({ ...payload, slug: form.slug }, session.csrf_token)
          : await updateAdminProject(project.id, payload, session.csrf_token);
      setProject(saved);
      setForm(asForm(saved));
      if (project === null) {
        router.replace(`/admin/projects/${saved.id}/edit`);
      } else {
        setMessage("Project details saved.");
      }
    } catch {
      setMessage("The project was not saved. Check required bilingual fields and try again.");
    } finally {
      setIsSaving(false);
    }
  };

  const saveBlocks = async () => {
    if (session === null || project === null) return;
    setIsSaving(true);
    setMessage(null);
    try {
      const saved = await replaceAdminProjectBlocks(project.id, blocks, session.csrf_token);
      setProject(saved);
      setBlocks(saved.blocks.map(asBlockWrite));
      setMessage("Editorial blocks saved.");
    } catch {
      setMessage("Editorial blocks were not saved. Check both language variants and try again.");
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) return <p className="admin-status">Loading project editor…</p>;
  if (options === null) return <p className="admin-status" role="alert">Project editor data is unavailable.</p>;

  return (
    <section className="admin-editor" aria-labelledby="admin-project-editor-title">
      <div className="admin-editor__heading">
        <div>
          <p className="admin-eyebrow">PROJECT EDITOR</p>
          <h1 id="admin-project-editor-title">{project === null ? "Create project" : project.title_en}</h1>
          {project !== null ? <p><code>/{project.slug}</code> is immutable after creation.</p> : null}
        </div>
        <Link href="/admin/projects">Back to projects</Link>
      </div>
      <div className="admin-editor__tabs" role="tablist" aria-label="Project editor sections">
        {tabs.map((tab) => (
          <button aria-selected={activeTab === tab} key={tab} onClick={() => setActiveTab(tab)} role="tab" type="button">
            {tab}
          </button>
        ))}
      </div>
      {message !== null ? <p className="admin-form__message" role="alert">{message}</p> : null}
      <form className="admin-editor__form" onSubmit={saveProject}>
        {activeTab === "General" ? (
          <div className="admin-editor__grid">
            {project === null ? <TextField label="Immutable slug" onChange={(value) => setText("slug", value)} required value={form.slug} /> : null}
            <TextField label="Title / EN" onChange={(value) => setText("title_en", value)} required value={form.title_en} />
            <TextField label="Title / FA" onChange={(value) => setText("title_fa", value)} required value={form.title_fa} />
            <TextField label="Subtitle / EN" onChange={(value) => setText("subtitle_en", value)} value={form.subtitle_en} />
            <TextField label="Subtitle / FA" onChange={(value) => setText("subtitle_fa", value)} value={form.subtitle_fa} />
            <TextField label="Summary / EN" multiline onChange={(value) => setText("summary_en", value)} required value={form.summary_en} />
            <TextField label="Summary / FA" multiline onChange={(value) => setText("summary_fa", value)} required value={form.summary_fa} />
            <TextField label="Location / EN" onChange={(value) => setText("location_en", value)} required value={form.location_en} />
            <TextField label="Location / FA" onChange={(value) => setText("location_fa", value)} required value={form.location_fa} />
            <label className="admin-editor__field"><span>Completion year</span><input max="9999" min="1000" onChange={(event) => setText("completion_year", event.target.value)} type="number" value={form.completion_year} /></label>
            <TextField label="Status / EN" onChange={(value) => setText("status_en", value)} value={form.status_en} />
            <TextField label="Status / FA" onChange={(value) => setText("status_fa", value)} value={form.status_fa} />
            <label className="admin-editor__toggle"><input checked={form.featured} onChange={(event) => setForm((current) => ({ ...current, featured: event.target.checked }))} type="checkbox" />Featured on home</label>
            <TaxonomyChecklist label="Disciplines" onChange={(discipline_ids) => setForm((current) => ({ ...current, discipline_ids }))} options={options.disciplines} selected={form.discipline_ids} />
            <TaxonomyChecklist label="Typologies" onChange={(typology_ids) => setForm((current) => ({ ...current, typology_ids }))} options={options.typologies} selected={form.typology_ids} />
          </div>
        ) : null}
        {activeTab === "Content" ? (
          <div className="admin-editor__grid">
            <TextField label="Introduction title / EN" onChange={(value) => setText("intro_title_en", value)} value={form.intro_title_en} />
            <TextField label="Introduction title / FA" onChange={(value) => setText("intro_title_fa", value)} value={form.intro_title_fa} />
            <TextField label="Introduction / EN" multiline onChange={(value) => setText("intro_en", value)} value={form.intro_en} />
            <TextField label="Introduction / FA" multiline onChange={(value) => setText("intro_fa", value)} value={form.intro_fa} />
            <TextField label="Narrative title / EN" onChange={(value) => setText("narrative_title_en", value)} value={form.narrative_title_en} />
            <TextField label="Narrative title / FA" onChange={(value) => setText("narrative_title_fa", value)} value={form.narrative_title_fa} />
            <TextField label="Narrative / EN" multiline onChange={(value) => setText("narrative_en", value)} value={form.narrative_en} />
            <TextField label="Narrative / FA" multiline onChange={(value) => setText("narrative_fa", value)} value={form.narrative_fa} />
            <TextField label="Quote / EN" multiline onChange={(value) => setText("quote_en", value)} value={form.quote_en} />
            <TextField label="Quote / FA" multiline onChange={(value) => setText("quote_fa", value)} value={form.quote_fa} />
            <TextField label="Material title / EN" onChange={(value) => setText("material_title_en", value)} value={form.material_title_en} />
            <TextField label="Material title / FA" onChange={(value) => setText("material_title_fa", value)} value={form.material_title_fa} />
            <TextField label="Material / EN" multiline onChange={(value) => setText("material_en", value)} value={form.material_en} />
            <TextField label="Material / FA" multiline onChange={(value) => setText("material_fa", value)} value={form.material_fa} />
            {project !== null ? <ProjectBlocksEditor blocks={blocks} disabled={isSaving} onChange={setBlocks} /> : <p>Save the project first to manage its structured editorial blocks.</p>}
            {project !== null ? <button disabled={isSaving} onClick={() => void saveBlocks()} type="button">Save editorial blocks</button> : null}
          </div>
        ) : null}
        {activeTab === "Details" ? (
          <div className="admin-editor__grid">
            <TextField label="Client / EN" onChange={(value) => setText("client_en", value)} value={form.client_en} />
            <TextField label="Client / FA" onChange={(value) => setText("client_fa", value)} value={form.client_fa} />
            <TextField label="Architect / EN" onChange={(value) => setText("architect_en", value)} value={form.architect_en} />
            <TextField label="Architect / FA" onChange={(value) => setText("architect_fa", value)} value={form.architect_fa} />
            <TextField label="Collaborators / EN" multiline onChange={(value) => setText("collaborators_en", value)} value={form.collaborators_en} />
            <TextField label="Collaborators / FA" multiline onChange={(value) => setText("collaborators_fa", value)} value={form.collaborators_fa} />
            <TextField label="Area / EN" onChange={(value) => setText("area_en", value)} value={form.area_en} />
            <TextField label="Area / FA" onChange={(value) => setText("area_fa", value)} value={form.area_fa} />
            <TextField label="Scope / EN" onChange={(value) => setText("scope_en", value)} value={form.scope_en} />
            <TextField label="Scope / FA" onChange={(value) => setText("scope_fa", value)} value={form.scope_fa} />
            <label className="admin-editor__field"><span>Completion date</span><input onChange={(event) => setText("completion_date", event.target.value)} type="date" value={form.completion_date} /></label>
          </div>
        ) : null}
        {activeTab === "Gallery" ? <p className="admin-editor__notice">The gallery is intentionally unavailable until media assets, upload validation, and derivative processing are implemented. It does not accept external image URLs.</p> : null}
        {activeTab === "SEO" ? (
          <div className="admin-editor__grid">
            <TextField label="SEO title / EN" onChange={(value) => setText("seo_title_en", value)} value={form.seo_title_en} />
            <TextField label="SEO title / FA" onChange={(value) => setText("seo_title_fa", value)} value={form.seo_title_fa} />
            <TextField label="Meta description / EN" multiline onChange={(value) => setText("seo_description_en", value)} value={form.seo_description_en} />
            <TextField label="Meta description / FA" multiline onChange={(value) => setText("seo_description_fa", value)} value={form.seo_description_fa} />
            <p className="admin-editor__notice">Empty SEO fields safely fall back to the localized title and summary.</p>
          </div>
        ) : null}
        {activeTab === "Publishing" ? (
          <div className="admin-editor__grid">
            <label className="admin-editor__field"><span>State</span><select onChange={(event) => setForm((current) => ({ ...current, publication_state: event.target.value as ProjectFormState["publication_state"] }))} value={form.publication_state}><option value="draft">Draft</option><option value="published">Published</option></select></label>
            <label className="admin-editor__field"><span>Publication date</span><input onChange={(event) => setText("published_at", event.target.value)} type="datetime-local" value={form.published_at} /></label>
            <p className="admin-editor__notice">Publishing verifies required content in both languages. Saving a draft never exposes it publicly.</p>
          </div>
        ) : null}
        <div className="admin-editor__footer">
          <button disabled={isSaving} type="submit">{isSaving ? "Saving…" : project === null ? "Create project" : "Save project"}</button>
        </div>
      </form>
    </section>
  );
}
