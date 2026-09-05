import { Link } from "@/i18n/navigation";

export default function NotFound() {
  return (
    <main className="not-found section-shell">
      <p>404</p>
      <h1>Page not found</h1>
      <Link className="text-link" href="/">
        Return home
      </Link>
    </main>
  );
}
