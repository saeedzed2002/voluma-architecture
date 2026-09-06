import { AdminStudioContentManager } from "@/components/admin/admin-studio-content-manager";
import { AdminShell } from "@/components/admin/admin-shell";

export default function AdminRecognitionPage() {
  return (
    <AdminShell>
      <AdminStudioContentManager kind="recognition" title="Recognition" />
    </AdminShell>
  );
}
