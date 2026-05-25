"use client";

import { Button } from "@/components/ui/button";
import { AlertTriangle, RefreshCw, ArrowLeft } from "lucide-react";
import Link from "next/link";

export default function ArticleDetailError({
  error,
  reset,
}: {
  error: Error;
  reset: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4 text-center p-6">
      <AlertTriangle className="w-12 h-12 text-destructive" />
      <h2 className="text-xl font-semibold">Detail Artikel Gagal Dimuat</h2>
      <p className="text-muted-foreground max-w-md">{error.message}</p>
      <div className="flex gap-3">
        <Button onClick={reset} variant="outline">
          <RefreshCw className="w-4 h-4 mr-1" /> Coba Lagi
        </Button>
        <Link href="/articles">
          <Button variant="outline">
            <ArrowLeft className="w-4 h-4 mr-1" /> Kembali
          </Button>
        </Link>
      </div>
    </div>
  );
}
