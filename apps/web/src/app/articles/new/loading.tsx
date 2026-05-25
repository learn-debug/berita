import { Skeleton } from "@/components/ui/skeleton";

export default function NewArticleLoading() {
  return (
    <div className="space-y-6 max-w-2xl">
      <div className="space-y-1">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-4 w-64" />
      </div>
      <Skeleton className="h-64 w-full rounded-xl" />
    </div>
  );
}
