import { AdminSettingsManager } from "@/components/admin/admin-settings-manager";
import { AdminShell } from "@/components/admin/admin-shell";

export default function AdminSettingsPage() {
  return (
    <AdminShell>
      <AdminSettingsManager />
    </AdminShell>
  );
}
