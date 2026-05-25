"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  LayoutDashboard,
  GitBranch,
  FileText,
  Settings,
  PenSquare,
  LogOut,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth";
import { Button } from "@/components/ui/button";

const links = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/pipeline", label: "Pipeline", icon: GitBranch },
  { href: "/articles", label: "Artikel", icon: FileText },
  { href: "/articles/new", label: "Input Artikel", icon: PenSquare },
  { href: "/settings", label: "Pengaturan", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { logout } = useAuth();

  return (
    <aside className="w-64 border-r bg-sidebar shrink-0 flex flex-col">
      <div className="p-4 border-b">
        <Link href="/dashboard" className="font-bold text-lg tracking-tight">
          NewsAgent
        </Link>
        <p className="text-xs text-muted-foreground mt-0.5">Dashboard Redaksi</p>
      </div>
      <nav className="p-2 space-y-1 flex-1">
        {links.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className={cn(
              "flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors",
              pathname === href
                ? "bg-sidebar-accent text-sidebar-accent-foreground font-medium"
                : "text-sidebar-foreground hover:bg-sidebar-accent/50"
            )}
          >
            <Icon className="w-4 h-4" />
            {label}
          </Link>
        ))}
      </nav>
      <div className="p-2 border-t">
        <Button
          variant="ghost"
          size="sm"
          className="w-full justify-start text-muted-foreground"
          onClick={() => {
            logout();
            router.push("/login");
          }}
        >
          <LogOut className="w-4 h-4 mr-2" />
          Keluar
        </Button>
      </div>
    </aside>
  );
}
