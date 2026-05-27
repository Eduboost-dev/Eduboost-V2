import ETLAdminDashboard from "@/components/admin/ETLAdminDashboard";
import ContentFactoryLiveDashboard from "@/components/admin/contentFactory/ContentFactoryLiveDashboard";

export default function ContentFactoryAdminPage() {
  if (process.env.NEXT_PUBLIC_CONTENT_FACTORY_MOCK === "true") {
    return <ETLAdminDashboard />;
  }
  return <ContentFactoryLiveDashboard />;
}
