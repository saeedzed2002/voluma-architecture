"use client";

import { type FormEvent, useEffect, useState } from "react";

import {
  type AdminJournalArticle,
  type AdminJournalArticleListItem,
  type AdminJournalCategory,
  type JournalArticleBlockWrite,
  type JournalArticleWrite,
  createAdminJournalArticle,
  createAdminJournalCategory,
  deleteAdminJournalArticle,
  deleteAdminJournalCategory,
  getAdminJournalArticle,
  getAdminJournalArticles,
  getAdminJournalCategories,
  reorderAdminJournalCategories,
  updateAdminJournalArticle,
  updateAdminJournalCategory,
} from "@/lib/admin-api";

import { useAdminSession } from "./admin-session-provider";

type ArticleForm = JournalArticleWrite & { slug: string };
type CategoryForm = Pick<AdminJournalCategory, "slug" | "title_en" | "title_fa">;

const emptyCategory: CategoryForm = { slug: "", title_en: "", title_fa: "" };

function textBlock(): JournalArticleBlockWrite {
  return {
    block_type: "text",
    content_en: { body: "" },
    content_fa: { body: "" },
  };
}

function emptyArticle(categoryId = ""): ArticleForm {
  return {
    blocks: [textBlock()],
    category_id: categoryId,
    cover_alt_en: null,
    cover_alt_fa: null,
    cover_image_url: null,
    excerpt_en: "",
    excerpt_fa: "",
    publication_state: "draft",
    published_at: null,
    reading_minutes: 1,
    seo_description_en: null,
    seo_description_fa: null,
    seo_title_en: null,
    seo_title_fa: null,
    slug: "",
    title_en: "",
    title_fa: "",
  };
}

function toArticleForm(article: AdminJournalArticle): ArticleForm {
  return {
    blocks: article.blocks.map(({ block_type, content_en, content_fa }) => ({
      block_type,
      content_en,
      content_fa,
    })) as JournalArticleBlockWrite[],
    category_id: article.category.id,
    cover_alt_en: article.cover_alt_en,
    cover_alt_fa: article.cover_alt_fa,
    cover_image_url: article.cover_image_url,
    excerpt_en: article.excerpt_en,
    excerpt_fa: article.excerpt_fa,
    publication_state: article.publication_state,
    published_at: article.published_at,
    reading_minutes: article.reading_minutes,
    seo_description_en: article.seo_description_en,
    seo_description_fa: article.seo_description_fa,
    seo_title_en: article.seo_title_en,
    seo_title_fa: article.seo_title_fa,
    slug: article.slug,
    title_en: article.title_en,
    title_fa: article.title_fa,
  };
}

function listItem(article: AdminJournalArticle): AdminJournalArticleListItem {
  return {
    category: article.category,
    id: article.id,
    publication_state: article.publication_state,
    published_at: article.published_at,
    slug: article.slug,
    title_en: article.title_en,
    title_fa: article.title_fa,
    updated_at: article.updated_at,
  };
}

export function AdminJournalManager() {
  const { session } = useAdminSession();
  const [articles, setArticles] = useState<AdminJournalArticleListItem[]>([]);
  const [articleForm, setArticleForm] = useState<ArticleForm>(emptyArticle());
  const [categories, setCategories] = useState<AdminJournalCategory[]>([]);
  const [categoryForm, setCategoryForm] = useState<CategoryForm>(emptyCategory);
  const [editingArticleId, setEditingArticleId] = useState<string | null>(null);
  const [editingCategoryId, setEditingCategoryId] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    void Promise.all([getAdminJournalCategories(), getAdminJournalArticles()])
      .then(([categoryResponse, articleResponse]) => {
        if (!active) return;
        setCategories(categoryResponse.items);
        setArticles(articleResponse.items);
        setArticleForm((current) =>
          current.category_id || categoryResponse.items.length === 0
            ? current
            : { ...current, category_id: categoryResponse.items[0].id },
        );
      })
      .catch(() => {
        if (active) setMessage("Journal content is unavailable.");
      });
    return () => {
      active = false;
    };
  }, []);

  const resetArticle = () => {
    setEditingArticleId(null);
    setArticleForm(emptyArticle(categories[0]?.id ?? ""));
  };

  const resetCategory = () => {
    setEditingCategoryId(null);
    setCategoryForm(emptyCategory);
  };

  const saveCategory = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (session === null) return;
    try {
      const saved =
        editingCategoryId === null
          ? await createAdminJournalCategory(categoryForm, session.csrf_token)
          : await updateAdminJournalCategory(editingCategoryId, categoryForm, session.csrf_token);
      setCategories((current) =>
        editingCategoryId === null
          ? [...current, saved]
          : current.map((category) => (category.id === saved.id ? saved : category)),
      );
      setMessage(editingCategoryId === null ? "Journal category created." : "Journal category saved.");
      resetCategory();
    } catch {
      setMessage("The journal category could not be saved. Slugs must be unique lowercase identifiers.");
    }
  };

  const moveCategory = async (index: number, offset: -1 | 1) => {
    if (session === null) return;
    const reordered = [...categories];
    [reordered[index], reordered[index + offset]] = [reordered[index + offset], reordered[index]];
    try {
      const response = await reorderAdminJournalCategories(
        reordered.map((category) => category.id),
        session.csrf_token,
      );
      setCategories(response.items);
    } catch {
      setMessage("Category order was not saved. Refresh before retrying.");
    }
  };

  const editCategory = (category: AdminJournalCategory) => {
    setEditingCategoryId(category.id);
    setCategoryForm({ slug: category.slug, title_en: category.title_en, title_fa: category.title_fa });
    setMessage(null);
  };

  const removeCategory = async (category: AdminJournalCategory) => {
    if (session === null || !window.confirm(`Delete “${category.title_en}”?`)) return;
    try {
      await deleteAdminJournalCategory(category.id, session.csrf_token);
      setCategories((current) => current.filter((item) => item.id !== category.id));
      if (editingCategoryId === category.id) resetCategory();
      setMessage("Journal category deleted.");
    } catch {
      setMessage("A category with journal articles cannot be deleted.");
    }
  };

  const replaceBlock = (index: number, block: JournalArticleBlockWrite) => {
    setArticleForm((current) => ({
      ...current,
      blocks: current.blocks.map((item, itemIndex) => (itemIndex === index ? block : item)),
    }));
  };

  const saveArticle = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (session === null) return;
    const { slug, ...payload } = articleForm;
    try {
      const saved =
        editingArticleId === null
          ? await createAdminJournalArticle({ ...payload, slug }, session.csrf_token)
          : await updateAdminJournalArticle(editingArticleId, payload, session.csrf_token);
      const updatedItem = listItem(saved);
      setArticles((current) =>
        editingArticleId === null
          ? [updatedItem, ...current]
          : current.map((article) => (article.id === updatedItem.id ? updatedItem : article)),
      );
      setMessage(
        editingArticleId === null
          ? saved.publication_state === "published"
            ? "Journal article published."
            : "Journal draft created."
          : "Journal article saved.",
      );
      resetArticle();
    } catch {
      setMessage(
        "Published articles need a category, bilingual title/excerpt, and at least one complete bilingual text or quote block.",
      );
    }
  };

  const editArticle = async (article: AdminJournalArticleListItem) => {
    try {
      const response = await getAdminJournalArticle(article.id);
      setEditingArticleId(response.id);
      setArticleForm(toArticleForm(response));
      setMessage(null);
    } catch {
      setMessage("The journal article could not be loaded.");
    }
  };

  const removeArticle = async (article: AdminJournalArticleListItem) => {
    if (session === null || !window.confirm(`Delete “${article.title_en || article.slug}”?`)) return;
    try {
      await deleteAdminJournalArticle(article.id, session.csrf_token);
      setArticles((current) => current.filter((item) => item.id !== article.id));
      if (editingArticleId === article.id) resetArticle();
      setMessage("Journal article deleted.");
    } catch {
      setMessage("The journal article could not be deleted.");
    }
  };

  return (
    <section className="admin-projects" aria-labelledby="journal-admin-title">
      <div className="admin-dashboard__heading">
        <p className="admin-eyebrow">EDITORIAL PUBLISHING</p>
        <h1 id="journal-admin-title">Journal</h1>
        <p>Manage ordered categories and bilingual articles. A published article is immediately public.</p>
      </div>

      <section className="admin-editor" aria-labelledby="journal-categories-title">
        <div className="admin-editor__heading">
          <p className="admin-eyebrow">CATEGORIES</p>
          <h2 id="journal-categories-title">Journal categories</h2>
        </div>
        <form className="admin-editor__grid" onSubmit={saveCategory}>
          <label className="admin-editor__field">
            <span>Slug</span>
            <input
              onChange={(event) => setCategoryForm((current) => ({ ...current, slug: event.target.value }))}
              value={categoryForm.slug}
            />
          </label>
          <label className="admin-editor__field">
            <span>Title / EN</span>
            <input
              onChange={(event) =>
                setCategoryForm((current) => ({ ...current, title_en: event.target.value }))
              }
              value={categoryForm.title_en}
            />
          </label>
          <label className="admin-editor__field">
            <span>Title / FA</span>
            <input
              dir="rtl"
              onChange={(event) =>
                setCategoryForm((current) => ({ ...current, title_fa: event.target.value }))
              }
              value={categoryForm.title_fa}
            />
          </label>
          <div className="admin-editor__actions">
            <button className="admin-primary-link" type="submit">
              {editingCategoryId === null ? "Create category" : "Save category"}
            </button>
            {editingCategoryId !== null ? (
              <button onClick={resetCategory} type="button">
                Cancel editing
              </button>
            ) : null}
          </div>
        </form>
        <ol className="admin-project-list">
          {categories.map((category, index) => (
            <li className="admin-project-row" key={category.id}>
              <div>
                <p className="admin-project-row__eyebrow">
                  {String(category.display_order + 1).padStart(2, "0")} · {category.slug}
                </p>
                <h3>{category.title_en}</h3>
                <p dir="rtl">{category.title_fa}</p>
              </div>
              <div className="admin-project-row__actions">
                <button disabled={index === 0} onClick={() => void moveCategory(index, -1)} type="button">
                  ↑
                </button>
                <button
                  disabled={index === categories.length - 1}
                  onClick={() => void moveCategory(index, 1)}
                  type="button"
                >
                  ↓
                </button>
                <button onClick={() => editCategory(category)} type="button">
                  Edit
                </button>
                <button className="admin-project-row__delete" onClick={() => void removeCategory(category)} type="button">
                  Delete
                </button>
              </div>
            </li>
          ))}
        </ol>
      </section>

      <section className="admin-editor" aria-labelledby="journal-articles-title">
        <div className="admin-editor__heading">
          <p className="admin-eyebrow">ARTICLES</p>
          <h2 id="journal-articles-title">Bilingual articles</h2>
          <p>Text and quote blocks are available now. Cover images will be selected from the media library in `Phase 5`.</p>
        </div>
        <form className="admin-editor__form" onSubmit={saveArticle}>
          <div className="admin-editor__grid">
            <label className="admin-editor__field">
              <span>Publication state</span>
              <select
                onChange={(event) =>
                  setArticleForm((current) => ({
                    ...current,
                    publication_state: event.target.value as ArticleForm["publication_state"],
                  }))
                }
                value={articleForm.publication_state}
              >
                <option value="draft">Draft</option>
                <option value="published">Published</option>
              </select>
            </label>
            <label className="admin-editor__field">
              <span>Category</span>
              <select
                onChange={(event) => setArticleForm((current) => ({ ...current, category_id: event.target.value }))}
                value={articleForm.category_id}
              >
                <option value="">Choose a category</option>
                {categories.map((category) => (
                  <option key={category.id} value={category.id}>
                    {category.title_en}
                  </option>
                ))}
              </select>
            </label>
            <label className="admin-editor__field">
              <span>Slug</span>
              <input
                disabled={editingArticleId !== null}
                onChange={(event) => setArticleForm((current) => ({ ...current, slug: event.target.value }))}
                value={articleForm.slug}
              />
            </label>
            <label className="admin-editor__field">
              <span>Reading minutes</span>
              <input
                min="1"
                onChange={(event) =>
                  setArticleForm((current) => ({
                    ...current,
                    reading_minutes: Number(event.target.value) || 1,
                  }))
                }
                type="number"
                value={articleForm.reading_minutes}
              />
            </label>
            <label className="admin-editor__field admin-editor__field--wide">
              <span>Title / EN</span>
              <input
                onChange={(event) => setArticleForm((current) => ({ ...current, title_en: event.target.value }))}
                value={articleForm.title_en}
              />
            </label>
            <label className="admin-editor__field admin-editor__field--wide">
              <span>Title / FA</span>
              <input
                dir="rtl"
                onChange={(event) => setArticleForm((current) => ({ ...current, title_fa: event.target.value }))}
                value={articleForm.title_fa}
              />
            </label>
            <label className="admin-editor__field admin-editor__field--wide">
              <span>Excerpt / EN</span>
              <textarea
                onChange={(event) => setArticleForm((current) => ({ ...current, excerpt_en: event.target.value }))}
                value={articleForm.excerpt_en}
              />
            </label>
            <label className="admin-editor__field admin-editor__field--wide">
              <span>Excerpt / FA</span>
              <textarea
                dir="rtl"
                onChange={(event) => setArticleForm((current) => ({ ...current, excerpt_fa: event.target.value }))}
                value={articleForm.excerpt_fa}
              />
            </label>
          </div>

          <fieldset className="admin-block-editor">
            <legend>Article blocks</legend>
            {articleForm.blocks.map((block, index) => (
              <div className="admin-block-editor__block" key={`${block.block_type}-${index}`}>
                <label className="admin-editor__field">
                  <span>Block type</span>
                  <select
                    onChange={(event) =>
                      replaceBlock(
                        index,
                        event.target.value === "quote"
                          ? {
                              block_type: "quote",
                              content_en: { quote: "" },
                              content_fa: { quote: "" },
                            }
                          : textBlock(),
                      )
                    }
                    value={block.block_type}
                  >
                    <option value="text">Text</option>
                    <option value="quote">Quote</option>
                  </select>
                </label>
                {block.block_type === "text" ? (
                  <>
                    <label className="admin-editor__field">
                      <span>Heading / EN</span>
                      <input
                        onChange={(event) =>
                          replaceBlock(index, {
                            ...block,
                            content_en: { ...block.content_en, heading: event.target.value || undefined },
                          })
                        }
                        value={block.content_en.heading ?? ""}
                      />
                    </label>
                    <label className="admin-editor__field">
                      <span>Heading / FA</span>
                      <input
                        dir="rtl"
                        onChange={(event) =>
                          replaceBlock(index, {
                            ...block,
                            content_fa: { ...block.content_fa, heading: event.target.value || undefined },
                          })
                        }
                        value={block.content_fa.heading ?? ""}
                      />
                    </label>
                    <label className="admin-editor__field admin-editor__field--wide">
                      <span>Body / EN</span>
                      <textarea
                        onChange={(event) =>
                          replaceBlock(index, {
                            ...block,
                            content_en: { ...block.content_en, body: event.target.value },
                          })
                        }
                        value={block.content_en.body}
                      />
                    </label>
                    <label className="admin-editor__field admin-editor__field--wide">
                      <span>Body / FA</span>
                      <textarea
                        dir="rtl"
                        onChange={(event) =>
                          replaceBlock(index, {
                            ...block,
                            content_fa: { ...block.content_fa, body: event.target.value },
                          })
                        }
                        value={block.content_fa.body}
                      />
                    </label>
                  </>
                ) : (
                  <>
                    <label className="admin-editor__field admin-editor__field--wide">
                      <span>Quote / EN</span>
                      <textarea
                        onChange={(event) =>
                          replaceBlock(index, {
                            ...block,
                            content_en: { ...block.content_en, quote: event.target.value },
                          })
                        }
                        value={block.content_en.quote}
                      />
                    </label>
                    <label className="admin-editor__field admin-editor__field--wide">
                      <span>Quote / FA</span>
                      <textarea
                        dir="rtl"
                        onChange={(event) =>
                          replaceBlock(index, {
                            ...block,
                            content_fa: { ...block.content_fa, quote: event.target.value },
                          })
                        }
                        value={block.content_fa.quote}
                      />
                    </label>
                  </>
                )}
                <button
                  onClick={() =>
                    setArticleForm((current) => ({
                      ...current,
                      blocks: current.blocks.filter((_, blockIndex) => blockIndex !== index),
                    }))
                  }
                  type="button"
                >
                  Remove block
                </button>
              </div>
            ))}
            <button
              onClick={() =>
                setArticleForm((current) => ({ ...current, blocks: [...current.blocks, textBlock()] }))
              }
              type="button"
            >
              Add text block
            </button>
          </fieldset>

          <fieldset className="admin-block-editor">
            <legend>SEO</legend>
            <div className="admin-editor__grid">
              <label className="admin-editor__field">
                <span>SEO title / EN</span>
                <input
                  onChange={(event) =>
                    setArticleForm((current) => ({
                      ...current,
                      seo_title_en: event.target.value || null,
                    }))
                  }
                  value={articleForm.seo_title_en ?? ""}
                />
              </label>
              <label className="admin-editor__field">
                <span>SEO title / FA</span>
                <input
                  dir="rtl"
                  onChange={(event) =>
                    setArticleForm((current) => ({
                      ...current,
                      seo_title_fa: event.target.value || null,
                    }))
                  }
                  value={articleForm.seo_title_fa ?? ""}
                />
              </label>
              <label className="admin-editor__field admin-editor__field--wide">
                <span>SEO description / EN</span>
                <textarea
                  onChange={(event) =>
                    setArticleForm((current) => ({
                      ...current,
                      seo_description_en: event.target.value || null,
                    }))
                  }
                  value={articleForm.seo_description_en ?? ""}
                />
              </label>
              <label className="admin-editor__field admin-editor__field--wide">
                <span>SEO description / FA</span>
                <textarea
                  dir="rtl"
                  onChange={(event) =>
                    setArticleForm((current) => ({
                      ...current,
                      seo_description_fa: event.target.value || null,
                    }))
                  }
                  value={articleForm.seo_description_fa ?? ""}
                />
              </label>
            </div>
          </fieldset>

          <footer className="admin-editor__footer">
            <button className="admin-primary-link" disabled={categories.length === 0} type="submit">
              {editingArticleId === null ? "Create journal draft" : "Save journal article"}
            </button>
            {editingArticleId !== null ? (
              <button onClick={resetArticle} type="button">
                Cancel editing
              </button>
            ) : null}
          </footer>
        </form>
        <ol className="admin-project-list">
          {articles.map((article) => (
            <li className="admin-project-row" key={article.id}>
              <div>
                <p className="admin-project-row__eyebrow">
                  {article.publication_state} · {article.category.title_en}
                </p>
                <h3>{article.title_en || article.slug}</h3>
                <p dir="rtl">{article.title_fa}</p>
              </div>
              <div className="admin-project-row__actions">
                <button onClick={() => void editArticle(article)} type="button">
                  Edit
                </button>
                <button className="admin-project-row__delete" onClick={() => void removeArticle(article)} type="button">
                  Delete
                </button>
              </div>
            </li>
          ))}
        </ol>
      </section>
      {message ? (
        <p className="admin-form__message" role="alert">
          {message}
        </p>
      ) : null}
    </section>
  );
}
