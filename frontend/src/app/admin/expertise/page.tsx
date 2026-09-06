import { AdminBilingualContentManager } from "@/components/admin/admin-bilingual-content-manager";
import { AdminShell } from "@/components/admin/admin-shell";

export default function AdminExpertisePage() {
  return (
    <AdminShell>
      <AdminBilingualContentManager
        description="Ordered bilingual capabilities. Publish only complete entries; media will be attached in the dedicated media phase."
        kind="expertise"
        title="Expertise"
      />
    </AdminShell>
  );
}
