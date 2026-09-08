import { AdminMediaLibrary } from "@/components/admin/admin-media-library";
import { AdminShell } from "@/components/admin/admin-shell";

export default function AdminMediaPage() {
  return (
    <AdminShell>
      <AdminMediaLibrary />
    </AdminShell>
  );
}
