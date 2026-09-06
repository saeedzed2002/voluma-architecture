import { AdminMessageManager } from "@/components/admin/admin-message-manager";
import { AdminShell } from "@/components/admin/admin-shell";

export default function AdminMessagesPage() {
  return (
    <AdminShell>
      <AdminMessageManager />
    </AdminShell>
  );
}
