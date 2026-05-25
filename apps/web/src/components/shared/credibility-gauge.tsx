"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function CredibilityGauge({
  score,
  size = "md",
}: {
  score: number | null;
  size?: "sm" | "md" | "lg";
}) {
  if (score === null) return null;

  const colors =
    score >= 0.75
      ? { bar: "bg-green-500", text: "text-green-700" }
      : score >= 0.5
        ? { bar: "bg-yellow-500", text: "text-yellow-700" }
        : { bar: "bg-red-500", text: "text-red-700" };

  const label =
    score >= 0.75 ? "Tinggi" : score >= 0.5 ? "Sedang" : "Rendah";

  const sizeClasses = size === "lg"
    ? { text: "text-5xl", bar: "h-5", container: "gap-4" }
    : size === "sm"
      ? { text: "text-xl", bar: "h-2", container: "gap-2" }
      : { text: "text-3xl", bar: "h-3", container: "gap-3" };

  return (
    <div className={`flex items-center ${sizeClasses.container}`} role="img" aria-label={`Skor kredibilitas: ${(score * 100).toFixed(0)} dari 100, ${label.toLowerCase()}`}>
      <div className={`${sizeClasses.text} font-bold ${colors.text}`}>
        {(score * 100).toFixed(0)}
      </div>
      <div className="flex-1 space-y-1">
        <div className={`w-full bg-secondary rounded-full ${sizeClasses.bar}`}>
          <div
            className={`${sizeClasses.bar} rounded-full transition-all ${colors.bar}`}
            style={{ width: `${score * 100}%` }}
          />
        </div>
        <p className={`text-xs ${colors.text} font-medium`}>{label}</p>
      </div>
    </div>
  );
}

export function CredibilityGaugeCard({
  score,
  breakdown,
}: {
  score: number | null;
  breakdown?: { label: string; score: number }[];
}) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium">Credibility Score</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {score !== null ? (
          <CredibilityGauge score={score} size="lg" />
        ) : (
          <p className="text-sm text-muted-foreground">Belum tersedia</p>
        )}
        {breakdown && breakdown.length > 0 && (
          <div className="space-y-2 border-t pt-3">
            {breakdown.map((b) => (
              <div key={b.label} className="flex items-center gap-2">
                <span className="text-xs text-muted-foreground w-24">{b.label}</span>
                <div className="flex-1 h-2 bg-secondary rounded-full">
                  <div
                    className="h-2 rounded-full bg-blue-500 transition-all"
                    style={{ width: `${b.score * 100}%` }}
                  />
                </div>
                <span className="text-xs font-mono">{(b.score * 100).toFixed(0)}</span>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
