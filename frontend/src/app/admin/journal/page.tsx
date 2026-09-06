import { AdminJournalManager } from "@/components/admin/admin-journal-manager";
import { AdminShell } from "@/components/admin/admin-shell";

export default function AdminJournalPage() {
  return (
    <AdminShell>
      <AdminJournalManager />
    </AdminShell>
  );
}
