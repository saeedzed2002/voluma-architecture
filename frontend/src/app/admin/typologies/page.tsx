import { AdminShell } from "@/components/admin/admin-shell";
import { AdminTaxonomyManager } from "@/components/admin/admin-taxonomy-manager";

export default function AdminTypologiesPage() {
  return <AdminShell><AdminTaxonomyManager kind="typologies" title="Typologies" /></AdminShell>;
}
