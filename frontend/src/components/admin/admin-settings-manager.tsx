"use client";

import { type FormEvent, useEffect, useState } from "react";

import {
  type AdminSiteSettings,
  type AdminSiteSettingsPrinciple,
  type AdminSiteSettingsSocialLink,
  type SiteSettingsWrite,
  getAdminSiteSettings,
  updateAdminSiteSettings,
} from "@/lib/admin-api";

import { useAdminSession } from "./admin-session-provider";

const emptyPrinciple: AdminSiteSettingsPrinciple = {
  body_en: "",
  body_fa: "",
  title_en: "",
  title_fa: "",
};

const emptySocialLink: AdminSiteSettingsSocialLink = { label: "", url: "" };

function optional(value: string | null) {
  const normalized = value?.trim() ?? "";
  return normalized || null;
}

function editablePayload(settings: AdminSiteSettings): SiteSettingsWrite {
  const payload = Object.fromEntries(
    Object.entries(settings).filter(([key]) => key !== "id" && key !== "updated_at"),
  ) as SiteSettingsWrite;
  return {
    ...payload,
    contact_address_en: optional(payload.contact_address_en),
    contact_address_fa: optional(payload.contact_address_fa),
    contact_email: optional(payload.contact_email),
    contact_phone: optional(payload.contact_phone),
    default_seo_description_en: optional(payload.default_seo_description_en),
    default_seo_description_fa: optional(payload.default_seo_description_fa),
    default_seo_title_en: optional(payload.default_seo_title_en),
    default_seo_title_fa: optional(payload.default_seo_title_fa),
    favicon_url: optional(payload.favicon_url),
    home_hero_alt_en: optional(payload.home_hero_alt_en),
    home_hero_alt_fa: optional(payload.home_hero_alt_fa),
    home_hero_image_url: optional(payload.home_hero_image_url),
    logo_url: optional(payload.logo_url),
    social_links: payload.social_links.map((link) => ({
      label: link.label.trim(),
      url: link.url.trim(),
    })),
    studio_principles: payload.studio_principles.map((principle) => ({
      body_en: principle.body_en.trim(),
      body_fa: principle.body_fa.trim(),
      title_en: principle.title_en.trim(),
      title_fa: principle.title_fa.trim(),
    })),
  };
}

export function AdminSettingsManager() {
  const { session } = useAdminSession();
  const [settings, setSettings] = useState<AdminSiteSettings | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    void getAdminSiteSettings()
      .then((response) => {
        if (active) setSettings(response);
      })
      .catch(() => {
        if (active) setMessage("Site settings are unavailable. Refresh to try again.");
      });
    return () => {
      active = false;
    };
  }, []);

  const save = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (settings === null || session === null) return;
    try {
      const saved = await updateAdminSiteSettings(editablePayload(settings), session.csrf_token);
      setSettings(saved);
      setMessage("Site settings saved. Public content cache was refreshed.");
    } catch {
      setMessage("Settings were not saved. Check the bilingual fields, media paths, and HTTPS social links.");
    }
  };

  const set = <K extends keyof AdminSiteSettings>(key: K, value: AdminSiteSettings[K]) => {
    setSettings((current) => (current === null ? current : { ...current, [key]: value }));
  };

  const updateSocial = (index: number, key: keyof AdminSiteSettingsSocialLink, value: string) => {
    if (settings === null) return;
    const socialLinks = settings.social_links.map((link, position) =>
      position === index ? { ...link, [key]: value } : link,
    );
    set("social_links", socialLinks);
  };

  const updatePrinciple = (
    index: number,
    key: keyof AdminSiteSettingsPrinciple,
    value: string,
  ) => {
    if (settings === null) return;
    const principles = settings.studio_principles.map((principle, position) =>
      position === index ? { ...principle, [key]: value } : principle,
    );
    set("studio_principles", principles);
  };

  if (settings === null) {
    return <p className="admin-status">{message ?? "Loading site settings…"}</p>;
  }

  return (
    <section className="admin-settings" aria-labelledby="settings-title">
      <div className="admin-dashboard__heading">
        <p className="admin-eyebrow">SITE CONTROL</p>
        <h1 id="settings-title">Settings</h1>
        <p>One protected record controls public identity, contact details, appearance, home copy, privacy text, and default metadata.</p>
      </div>
      <form className="admin-settings__form" onSubmit={save}>
        <fieldset className="admin-settings__section">
          <legend>Brand, contact, and appearance</legend>
          <div className="admin-editor__grid">
            <label className="admin-editor__field">
              <span>Studio name</span>
              <input onChange={(event) => set("studio_name", event.target.value)} value={settings.studio_name} />
            </label>
            <label className="admin-editor__field">
              <span>Default theme</span>
              <select onChange={(event) => set("default_theme", event.target.value as AdminSiteSettings["default_theme"])} value={settings.default_theme}>
                <option value="system">System</option>
                <option value="light">Light</option>
                <option value="dark">Dark</option>
              </select>
            </label>
            <label className="admin-editor__field">
              <span>Logo public media path</span>
              <input onChange={(event) => set("logo_url", event.target.value)} placeholder="/media/logo.svg" value={settings.logo_url ?? ""} />
            </label>
            <label className="admin-editor__field">
              <span>Favicon public media path</span>
              <input onChange={(event) => set("favicon_url", event.target.value)} placeholder="/media/favicon.svg" value={settings.favicon_url ?? ""} />
            </label>
            <label className="admin-editor__field">
              <span>Contact email</span>
              <input onChange={(event) => set("contact_email", event.target.value)} type="email" value={settings.contact_email ?? ""} />
            </label>
            <label className="admin-editor__field">
              <span>Contact phone</span>
              <input onChange={(event) => set("contact_phone", event.target.value)} type="tel" value={settings.contact_phone ?? ""} />
            </label>
            <label className="admin-editor__field">
              <span>Address / EN</span>
              <textarea onChange={(event) => set("contact_address_en", event.target.value)} value={settings.contact_address_en ?? ""} />
            </label>
            <label className="admin-editor__field">
              <span>Address / FA</span>
              <textarea dir="rtl" onChange={(event) => set("contact_address_fa", event.target.value)} value={settings.contact_address_fa ?? ""} />
            </label>
          </div>
          <div className="admin-settings__collection">
            <div className="admin-settings__collection-heading">
              <h2>Social links</h2>
              <button onClick={() => set("social_links", [...settings.social_links, emptySocialLink])} type="button">Add link</button>
            </div>
            {settings.social_links.map((link, index) => (
              <div className="admin-settings__pair" key={`${link.label}-${index}`}>
                <label className="admin-editor__field">
                  <span>Label</span>
                  <input onChange={(event) => updateSocial(index, "label", event.target.value)} value={link.label} />
                </label>
                <label className="admin-editor__field">
                  <span>HTTPS URL</span>
                  <input onChange={(event) => updateSocial(index, "url", event.target.value)} type="url" value={link.url} />
                </label>
                <button className="admin-project-row__delete" onClick={() => set("social_links", settings.social_links.filter((_, position) => position !== index))} type="button">Remove</button>
              </div>
            ))}
          </div>
        </fieldset>

        <fieldset className="admin-settings__section">
          <legend>Default SEO</legend>
          <div className="admin-editor__grid">
            <label className="admin-editor__field">
              <span>Title / EN</span>
              <input onChange={(event) => set("default_seo_title_en", event.target.value)} value={settings.default_seo_title_en ?? ""} />
            </label>
            <label className="admin-editor__field">
              <span>Title / FA</span>
              <input dir="rtl" onChange={(event) => set("default_seo_title_fa", event.target.value)} value={settings.default_seo_title_fa ?? ""} />
            </label>
            <label className="admin-editor__field admin-editor__field--wide">
              <span>Description / EN</span>
              <textarea onChange={(event) => set("default_seo_description_en", event.target.value)} value={settings.default_seo_description_en ?? ""} />
            </label>
            <label className="admin-editor__field admin-editor__field--wide">
              <span>Description / FA</span>
              <textarea dir="rtl" onChange={(event) => set("default_seo_description_fa", event.target.value)} value={settings.default_seo_description_fa ?? ""} />
            </label>
          </div>
        </fieldset>

        <fieldset className="admin-settings__section">
          <legend>Home and studio</legend>
          <div className="admin-editor__grid">
            <label className="admin-editor__field admin-editor__field--wide"><span>Home title / EN</span><textarea onChange={(event) => set("home_title_en", event.target.value)} value={settings.home_title_en} /></label>
            <label className="admin-editor__field admin-editor__field--wide"><span>Home title / FA</span><textarea dir="rtl" onChange={(event) => set("home_title_fa", event.target.value)} value={settings.home_title_fa} /></label>
            <label className="admin-editor__field admin-editor__field--wide"><span>Home body / EN</span><textarea onChange={(event) => set("home_body_en", event.target.value)} value={settings.home_body_en} /></label>
            <label className="admin-editor__field admin-editor__field--wide"><span>Home body / FA</span><textarea dir="rtl" onChange={(event) => set("home_body_fa", event.target.value)} value={settings.home_body_fa} /></label>
            <label className="admin-editor__field"><span>Hero public media path</span><input onChange={(event) => set("home_hero_image_url", event.target.value)} value={settings.home_hero_image_url ?? ""} /></label>
            <label className="admin-editor__field"><span>Hero alt / EN</span><input onChange={(event) => set("home_hero_alt_en", event.target.value)} value={settings.home_hero_alt_en ?? ""} /></label>
            <label className="admin-editor__field"><span>Hero alt / FA</span><input dir="rtl" onChange={(event) => set("home_hero_alt_fa", event.target.value)} value={settings.home_hero_alt_fa ?? ""} /></label>
            <label className="admin-editor__field admin-editor__field--wide"><span>Studio introduction / EN</span><textarea onChange={(event) => set("studio_intro_en", event.target.value)} value={settings.studio_intro_en} /></label>
            <label className="admin-editor__field admin-editor__field--wide"><span>Studio introduction / FA</span><textarea dir="rtl" onChange={(event) => set("studio_intro_fa", event.target.value)} value={settings.studio_intro_fa} /></label>
          </div>
          <div className="admin-settings__collection">
            <div className="admin-settings__collection-heading">
              <h2>Studio principles</h2>
              <button onClick={() => set("studio_principles", [...settings.studio_principles, emptyPrinciple])} type="button">Add principle</button>
            </div>
            {settings.studio_principles.map((principle, index) => (
              <div className="admin-settings__principle" key={`${principle.title_en}-${index}`}>
                <label className="admin-editor__field"><span>Title / EN</span><input onChange={(event) => updatePrinciple(index, "title_en", event.target.value)} value={principle.title_en} /></label>
                <label className="admin-editor__field"><span>Title / FA</span><input dir="rtl" onChange={(event) => updatePrinciple(index, "title_fa", event.target.value)} value={principle.title_fa} /></label>
                <label className="admin-editor__field"><span>Body / EN</span><textarea onChange={(event) => updatePrinciple(index, "body_en", event.target.value)} value={principle.body_en} /></label>
                <label className="admin-editor__field"><span>Body / FA</span><textarea dir="rtl" onChange={(event) => updatePrinciple(index, "body_fa", event.target.value)} value={principle.body_fa} /></label>
                <button className="admin-project-row__delete" onClick={() => set("studio_principles", settings.studio_principles.filter((_, position) => position !== index))} type="button">Remove</button>
              </div>
            ))}
          </div>
        </fieldset>

        <fieldset className="admin-settings__section">
          <legend>Privacy</legend>
          <div className="admin-editor__grid">
            <label className="admin-editor__field admin-editor__field--wide"><span>Privacy text / EN</span><textarea onChange={(event) => set("privacy_en", event.target.value)} value={settings.privacy_en} /></label>
            <label className="admin-editor__field admin-editor__field--wide"><span>Privacy text / FA</span><textarea dir="rtl" onChange={(event) => set("privacy_fa", event.target.value)} value={settings.privacy_fa} /></label>
          </div>
        </fieldset>

        <div className="admin-editor__actions">
          <button className="admin-primary-link" type="submit">Save settings</button>
          {message ? <p className="admin-form__message" role="status">{message}</p> : null}
        </div>
      </form>
    </section>
  );
}
