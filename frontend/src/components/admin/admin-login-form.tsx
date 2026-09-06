"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { AdminApiError, loginAdministrator } from "@/lib/admin-api";

import { useAdminSession } from "./admin-session-provider";

export function AdminLoginForm() {
  const router = useRouter();
  const { setSession } = useAdminSession();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setMessage(null);
    try {
      const session = await loginAdministrator(email, password);
      setSession(session);
      router.replace("/admin");
    } catch (error: unknown) {
      if (error instanceof AdminApiError && error.status === 429) {
        setMessage("Too many attempts. Try again later.");
      } else {
        setMessage("The email or password is not valid.");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="admin-login" id="main-content">
      <section aria-labelledby="admin-login-title" className="admin-login__panel">
        <p className="admin-eyebrow">VOLUMA / ADMINISTRATION</p>
        <h1 id="admin-login-title">Sign in</h1>
        <p className="admin-login__intro">Use an administrator account. Sessions expire after eight hours.</p>
        <form className="admin-form" onSubmit={submit}>
          <label>
            <span>Email</span>
            <input
              autoComplete="username"
              onChange={(event) => setEmail(event.target.value)}
              required
              type="email"
              value={email}
            />
          </label>
          <label>
            <span>Password</span>
            <input
              autoComplete="current-password"
              minLength={12}
              onChange={(event) => setPassword(event.target.value)}
              required
              type="password"
              value={password}
            />
          </label>
          {message !== null ? <p className="admin-form__message" role="alert">{message}</p> : null}
          <button disabled={isSubmitting} type="submit">
            {isSubmitting ? "Signing in…" : "Sign in"}
          </button>
        </form>
      </section>
    </main>
  );
}
