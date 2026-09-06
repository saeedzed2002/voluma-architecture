import { AdminProjectList } from "@/components/admin/admin-project-list";
import { AdminShell } from "@/components/admin/admin-shell";

export default function AdminProjectsPage() {
  return (
    <AdminShell>
      <AdminProjectList />
    </AdminShell>
  );
}
