import type { Metadata } from "next";
import type { ReactNode } from "react";

import { AdminSessionProvider } from "@/components/admin/admin-session-provider";

import { instrumentSans } from "../fonts";
import "../globals.css";

export const metadata: Metadata = {
  robots: { follow: false, index: false },
  title: "Administration — VOLUMA",
};

export default function AdminLayout({ children }: { children: ReactNode }) {
  return (
    <html className={instrumentSans.variable} lang="en">
      <body className="admin-root">
        <a className="skip-link" href="#main-content">
          Skip to main content
        </a>
        <AdminSessionProvider>{children}</AdminSessionProvider>
      </body>
    </html>
  );
}
