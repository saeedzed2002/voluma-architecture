import { AdminShell } from "@/components/admin/admin-shell";
import { AdminTaxonomyManager } from "@/components/admin/admin-taxonomy-manager";

export default function AdminDisciplinesPage() {
  return <AdminShell><AdminTaxonomyManager kind="disciplines" title="Disciplines" /></AdminShell>;
}
