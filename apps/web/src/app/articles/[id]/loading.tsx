import { Skeleton } from "@/components/ui/skeleton";

export default function ArticleDetailLoading() {
  return (
    <div className="space-y-6 max-w-3xl">
      <Skeleton className="h-7 w-24 rounded-md" />
      <div className="space-y-1">
        <Skeleton className="h-8 w-full" />
        <Skeleton className="h-4 w-48" />
      </div>
      <Skeleton className="h-64 w-full rounded-xl" />
      <div className="space-y-2">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-5/6" />
        <Skeleton className="h-4 w-4/6" />
      </div>
    </div>
  );
}
