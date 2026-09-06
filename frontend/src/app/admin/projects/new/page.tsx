import { AdminProjectEditor } from "@/components/admin/admin-project-editor";
import { AdminShell } from "@/components/admin/admin-shell";

export default function NewAdminProjectPage() {
  return (
    <AdminShell>
      <AdminProjectEditor />
    </AdminShell>
  );
}
