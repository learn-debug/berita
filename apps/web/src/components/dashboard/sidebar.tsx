"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import {
  LayoutDashboard,
  GitBranch,
  FileText,
  Settings,
  PenSquare,
  LogOut,
  Menu,
  X,
  Users,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { ThemeToggle } from "@/components/shared/theme-toggle";

const links = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/pipeline", label: "Pipeline", icon: GitBranch },
  { href: "/articles", label: "Artikel", icon: FileText },
  { href: "/articles/new", label: "Input Artikel", icon: PenSquare },
];

const ownerLinks = [
  { href: "/users", label: "Pengguna", icon: Users },
  { href: "/settings", label: "Pengaturan", icon: Settings },
];

function isActive(pathname: string, href: string): boolean {
  if (href === "/dashboard") return pathname === "/dashboard";
  return pathname.startsWith(href);
}

function SidebarContent() {
  const pathname = usePathname();
  const { logout, isOwner, user } = useAuth();

  return (
    <>
      <div className="p-4 border-b">
        <Link href="/dashboard" className="font-bold text-lg tracking-tight">
          NewsAgent
        </Link>
        <p className="text-xs text-muted-foreground mt-0.5">Dashboard Redaksi</p>
        {user && (
          <p className="text-xs text-muted-foreground mt-1">
            {user.name || user.email} · {isOwner ? "Owner" : "Editor"}
          </p>
        )}
      </div>
      <nav className="p-2 space-y-1 flex-1" aria-label="Navigasi utama">
        {links.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className={cn(
              "flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors",
              isActive(pathname, href)
                ? "bg-sidebar-accent text-sidebar-accent-foreground font-medium"
                : "text-sidebar-foreground hover:bg-sidebar-accent/50"
            )}
          >
            <Icon className="w-4 h-4 shrink-0" />
            {label}
          </Link>
        ))}
        {isOwner && ownerLinks.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className={cn(
              "flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors",
              isActive(pathname, href)
                ? "bg-sidebar-accent text-sidebar-accent-foreground font-medium"
                : "text-sidebar-foreground hover:bg-sidebar-accent/50"
            )}
          >
            <Icon className="w-4 h-4 shrink-0" />
            {label}
          </Link>
        ))}
      </nav>
      <div className="p-2 border-t space-y-1">
        <ThemeToggle />
        <Button
          variant="ghost"
          size="sm"
          className="w-full justify-start text-muted-foreground"
          aria-label="Keluar"
          onClick={() => {
            logout();
          }}
        >
          <LogOut className="w-4 h-4 mr-2 shrink-0" />
          Keluar
        </Button>
      </div>
    </>
  );
}

export function Sidebar() {
  const [open, setOpen] = useState(false);

  return (
    <>
      <div className="lg:hidden fixed top-0 left-0 right-0 z-50 flex items-center justify-between p-3 border-b bg-background">
        <Link href="/dashboard" className="font-bold text-base tracking-tight">
          NewsAgent
        </Link>
        <Sheet open={open} onOpenChange={setOpen}>
          <SheetTrigger render={<Button variant="ghost" size="icon" aria-label="Buka menu navigasi" />}>
            {open ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </SheetTrigger>
          <SheetContent side="left" className="w-64 p-0">
            <SidebarContent />
          </SheetContent>
        </Sheet>
      </div>

      <aside className="hidden lg:flex w-64 border-r bg-sidebar shrink-0 flex-col">
        <SidebarContent />
      </aside>
    </>
  );
}
