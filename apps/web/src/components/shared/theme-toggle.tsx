"use client";

import { Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { Button } from "@/components/ui/button";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  return (
    <Button
      variant="ghost"
      size="sm"
      className="w-full justify-start text-muted-foreground"
      aria-label={theme === "dark" ? "Mode terang" : "Mode gelap"}
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
    >
      <Sun className="w-4 h-4 mr-2 hidden dark:inline" />
      <Moon className="w-4 h-4 mr-2 inline dark:hidden" />
      {theme === "dark" ? "Mode Terang" : "Mode Gelap"}
    </Button>
  );
}
