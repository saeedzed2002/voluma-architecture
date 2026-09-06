import { AdminStudioContentManager } from "@/components/admin/admin-studio-content-manager";
import { AdminShell } from "@/components/admin/admin-shell";

export default function AdminPeoplePage() {
  return (
    <AdminShell>
      <AdminStudioContentManager kind="people" title="People" />
    </AdminShell>
  );
}
