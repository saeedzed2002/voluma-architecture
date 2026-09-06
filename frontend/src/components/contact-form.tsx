"use client";

import { type FormEvent, useEffect, useRef, useState } from "react";

import type { Locale } from "@/i18n/routing";

type ContactFormProps = {
  locale: Locale;
};

const labels = {
  en: {
    company: "Company (optional)",
    email: "Email address",
    message: "Tell us about the place or question",
    name: "Name",
    phone: "Phone (optional)",
    projectType: "Project type (optional)",
    selectProjectType: "Select a project type",
    error: "We could not send your enquiry right now. Please try again shortly.",
    rateLimited: "Please wait before sending another enquiry.",
    submittedTooQuickly: "Please take a moment to complete the form before sending it.",
    success: "Thank you. Your enquiry has been received.",
    submit: "Send enquiry",
  },
  fa: {
    company: "شرکت (اختیاری)",
    email: "نشانی ایمیل",
    message: "از مکان یا پرسش خود بگویید",
    name: "نام",
    phone: "تلفن (اختیاری)",
    projectType: "نوع پروژه (اختیاری)",
    selectProjectType: "نوع پروژه را انتخاب کنید",
    error: "ارسال درخواست اکنون ممکن نیست. لطفاً کمی بعد دوباره تلاش کنید.",
    rateLimited: "لطفاً پیش از ارسال درخواست دیگر کمی صبر کنید.",
    submittedTooQuickly: "لطفاً پیش از ارسال فرم، کمی برای تکمیل آن زمان بگذارید.",
    success: "سپاسگزاریم. درخواست شما دریافت شد.",
    submit: "ارسال درخواست",
  },
} as const;

export function ContactForm({ locale }: ContactFormProps) {
  const copy = labels[locale];
  const startedAt = useRef<number | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [status, setStatus] = useState<string | null>(null);

  useEffect(() => {
    startedAt.current = Date.now();
  }, []);

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (isSubmitting) return;
    const form = event.currentTarget;
    const data = new FormData(form);
    setIsSubmitting(true);
    setStatus(null);
    try {
      const response = await fetch("/api/v1/contact", {
        body: JSON.stringify({
          company: String(data.get("company") ?? "") || null,
          email: String(data.get("email") ?? ""),
          message: String(data.get("message") ?? ""),
          name: String(data.get("name") ?? ""),
          phone: String(data.get("phone") ?? "") || null,
          project_type: String(data.get("projectType") ?? "") || null,
          source_locale: locale,
          started_at: startedAt.current ?? Date.now(),
          website: String(data.get("website") ?? ""),
        }),
        headers: { "Content-Type": "application/json" },
        method: "POST",
      });
      if (response.ok) {
        form.reset();
        startedAt.current = Date.now();
        setStatus(copy.success);
      } else if (response.status === 429) {
        setStatus(copy.rateLimited);
      } else if (response.status === 422) {
        setStatus(copy.submittedTooQuickly);
      } else {
        setStatus(copy.error);
      }
    } catch {
      setStatus(copy.error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form className="contact-form" onSubmit={(event) => void submit(event)}>
      <div className="contact-form__honeypot" aria-hidden="true">
        <label htmlFor="website">Website</label>
        <input autoComplete="off" id="website" name="website" tabIndex={-1} type="text" />
      </div>
      <label>
        <span>{copy.name}</span>
        <input autoComplete="name" name="name" required type="text" />
      </label>
      <label>
        <span>{copy.email}</span>
        <input autoComplete="email" name="email" required type="email" />
      </label>
      <label>
        <span>{copy.phone}</span>
        <input autoComplete="tel" name="phone" type="tel" />
      </label>
      <label>
        <span>{copy.company}</span>
        <input autoComplete="organization" name="company" type="text" />
      </label>
      <label>
        <span>{copy.projectType}</span>
        <select defaultValue="" name="projectType">
          <option value="">{copy.selectProjectType}</option>
          <option value="architecture">{locale === "fa" ? "معماری" : "Architecture"}</option>
          <option value="interior">
            {locale === "fa" ? "معماری داخلی" : "Interior architecture"}
          </option>
          <option value="reuse">{locale === "fa" ? "باززنده‌سازی" : "Adaptive reuse"}</option>
        </select>
      </label>
      <label className="contact-form__message">
        <span>{copy.message}</span>
        <textarea name="message" required rows={7} />
      </label>
      <div className="contact-form__actions">
        <button disabled={isSubmitting} type="submit">
          {copy.submit}
        </button>
        {status !== null ? (
          <p aria-live="polite" role="status">
            {status}
          </p>
        ) : null}
      </div>
    </form>
  );
}
