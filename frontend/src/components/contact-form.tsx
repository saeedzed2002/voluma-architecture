"use client";

import { useState } from "react";

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
    status:
      "This development preview does not transmit or store contact messages. The secured contact service is scheduled for a later phase.",
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
    status:
      "این پیش‌نمایش توسعه، پیام‌های تماس را ارسال یا ذخیره نمی‌کند. سرویس امن تماس در مرحله‌ای بعد پیاده‌سازی می‌شود.",
    submit: "ارسال درخواست",
  },
} as const;

export function ContactForm({ locale }: ContactFormProps) {
  const copy = labels[locale];
  const [statusVisible, setStatusVisible] = useState(false);

  return (
    <form
      className="contact-form"
      onSubmit={(event) => {
        event.preventDefault();
        setStatusVisible(true);
      }}
    >
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
        <button type="submit">{copy.submit}</button>
        {statusVisible ? (
          <p aria-live="polite" role="status">
            {copy.status}
          </p>
        ) : null}
      </div>
    </form>
  );
}
