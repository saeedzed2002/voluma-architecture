import { AdminProjectEditor } from "@/components/admin/admin-project-editor";
import { AdminShell } from "@/components/admin/admin-shell";

type AdminProjectEditPageProps = {
  params: Promise<{ id: string }>;
};

export default async function AdminProjectEditPage({ params }: AdminProjectEditPageProps) {
  const { id } = await params;
  return (
    <AdminShell>
      <AdminProjectEditor projectId={id} />
    </AdminShell>
  );
}
