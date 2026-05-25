import { Skeleton } from "@/components/ui/skeleton";

export default function SettingsLoading() {
  return (
    <div className="space-y-6 max-w-3xl">
      <div className="space-y-1">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-4 w-56" />
      </div>
      <Skeleton className="h-10 w-96 rounded-lg" />
      <Skeleton className="h-96 w-full rounded-xl" />
    </div>
  );
}
