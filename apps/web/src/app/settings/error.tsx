"use client";

import { Button } from "@/components/ui/button";
import { AlertTriangle, RefreshCw } from "lucide-react";

export default function SettingsError({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4 text-center p-6">
      <AlertTriangle className="w-12 h-12 text-destructive" />
      <h2 className="text-xl font-semibold">Pengaturan Gagal Dimuat</h2>
      <p className="text-muted-foreground max-w-md">{error.message}</p>
      <Button onClick={reset} variant="outline">
        <RefreshCw className="w-4 h-4 mr-1" /> Coba Lagi
      </Button>
    </div>
  );
}
