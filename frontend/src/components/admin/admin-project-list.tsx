"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import {
  type AdminProjectListItem,
  deleteAdminProject,
  getAdminProjects,
  reorderAdminProjects,
} from "@/lib/admin-api";

import { useAdminSession } from "./admin-session-provider";

function ProjectRow({
  index,
  item,
  onDelete,
  onMove,
  total,
}: {
  index: number;
  item: AdminProjectListItem;
  onDelete: (projectId: string) => void;
  onMove: (index: number, offset: -1 | 1) => void;
  total: number;
}) {
  return (
    <li className="admin-project-row">
      <div>
        <p className="admin-project-row__eyebrow">
          {item.publication_state === "published" ? "Published" : "Draft"} / {item.display_order + 1}
        </p>
        <h2>{item.title_en}</h2>
        <p dir="rtl">{item.title_fa}</p>
        <code>/{item.slug}</code>
      </div>
      <div className="admin-project-row__actions">
        <button aria-label={`Move ${item.title_en} earlier`} disabled={index === 0} onClick={() => onMove(index, -1)} type="button">
          ↑
        </button>
        <button aria-label={`Move ${item.title_en} later`} disabled={index === total - 1} onClick={() => onMove(index, 1)} type="button">
          ↓
        </button>
        <Link href={`/admin/projects/${item.id}/edit`}>Edit</Link>
        <button className="admin-project-row__delete" onClick={() => onDelete(item.id)} type="button">
          Delete
        </button>
      </div>
    </li>
  );
}

export function AdminProjectList() {
  const { session } = useAdminSession();
  const [items, setItems] = useState<AdminProjectListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isMutating, setIsMutating] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    let active = true;
    async function loadProjects() {
      try {
        const response = await getAdminProjects();
        if (active) {
          setItems(response.items);
          setMessage(null);
        }
      } catch {
        if (active) setMessage("Projects are unavailable. Refresh to try again.");
      } finally {
        if (active) setIsLoading(false);
      }
    }
    void loadProjects();
    return () => {
      active = false;
    };
  }, [refreshKey]);

  const move = async (index: number, offset: -1 | 1) => {
    if (session === null) return;
    const next = [...items];
    const target = index + offset;
    [next[index], next[target]] = [next[target], next[index]];
    setIsMutating(true);
    setMessage(null);
    try {
      const response = await reorderAdminProjects(
        next.map((item) => item.id),
        session.csrf_token,
      );
      setItems(response.items);
    } catch {
      setMessage("The order was not saved. Refresh before trying again.");
    } finally {
      setIsMutating(false);
    }
  };

  const remove = async (projectId: string) => {
    if (session === null) return;
    const project = items.find((item) => item.id === projectId);
    if (project === undefined) return;
    if (!window.confirm(`Delete “${project.title_en}”? This cannot be undone.`)) return;
    setIsMutating(true);
    setMessage(null);
    try {
      await deleteAdminProject(projectId, session.csrf_token);
      setItems((current) => current.filter((item) => item.id !== projectId));
    } catch {
      setMessage("The project was not deleted. Refresh before trying again.");
    } finally {
      setIsMutating(false);
    }
  };

  return (
    <section className="admin-projects" aria-labelledby="admin-projects-title">
      <div className="admin-dashboard__heading">
        <p className="admin-eyebrow">CONTENT CONTROL</p>
        <h1 id="admin-projects-title">Projects</h1>
        <p>Drafts are private. Ordering updates all projects atomically.</p>
      </div>
      <div className="admin-projects__toolbar">
        <button disabled={isLoading || isMutating} onClick={() => setRefreshKey((current) => current + 1)} type="button">
          Refresh
        </button>
        <Link className="admin-primary-link" href="/admin/projects/new">
          Create project
        </Link>
      </div>
      {message !== null ? <p role="alert">{message}</p> : null}
      {isLoading ? <p>Loading projects…</p> : null}
      {!isLoading && items.length === 0 ? <p>No projects exist yet.</p> : null}
      {items.length > 0 ? (
        <ol className="admin-project-list">
          {items.map((item, index) => (
            <ProjectRow index={index} item={item} key={item.id} onDelete={remove} onMove={move} total={items.length} />
          ))}
        </ol>
      ) : null}
    </section>
  );
}
