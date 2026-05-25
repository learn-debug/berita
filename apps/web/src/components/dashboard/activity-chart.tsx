"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

interface DayData {
  date: string;
  label: string;
  published: number;
  review: number;
  failed: number;
}

export function ActivityChart({ data }: { data: DayData[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm font-medium">Aktivitas Pipeline (7 Hari)</CardTitle>
      </CardHeader>
      <CardContent>
        {data.length > 0 ? (
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="label" tick={{ fontSize: 11 }} />
              <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="published" name="Published" fill="#22c55e" radius={[2, 2, 0, 0]} stackId="a" />
              <Bar dataKey="review" name="Review" fill="#eab308" radius={[2, 2, 0, 0]} stackId="a" />
              <Bar dataKey="failed" name="Gagal" fill="#ef4444" radius={[2, 2, 0, 0]} stackId="a" />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-sm text-muted-foreground">Belum ada data 7 hari terakhir.</p>
        )}
      </CardContent>
    </Card>
  );
}
