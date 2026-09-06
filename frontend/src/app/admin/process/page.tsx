import { AdminBilingualContentManager } from "@/components/admin/admin-bilingual-content-manager";
import { AdminShell } from "@/components/admin/admin-shell";

export default function AdminProcessPage() {
  return (
    <AdminShell>
      <AdminBilingualContentManager
        description="Ordered bilingual design steps. Publish only complete entries; optional images belong to the dedicated media phase."
        kind="process"
        title="Process"
      />
    </AdminShell>
  );
}
