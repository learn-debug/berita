import Link from "next/link"
import { Newspaper } from "lucide-react"

export function Navbar() {
  return (
    <header className="border-b border-border bg-background/95 sticky top-0 z-50 backdrop-blur">
      <div className="container flex h-16 items-center justify-between">
        <Link href="/" className="flex items-center gap-2 font-semibold text-lg no-underline text-foreground">
          <Newspaper className="size-6 text-primary" />
          <span>NewsAgent</span>
        </Link>
        <nav className="flex items-center gap-6 text-sm">
          <Link href="/" className="text-muted-foreground hover:text-foreground no-underline transition-colors">
            Beranda
          </Link>
          <Link href="/tentang" className="text-muted-foreground hover:text-foreground no-underline transition-colors">
            Tentang
          </Link>
        </nav>
      </div>
    </header>
  )
}
