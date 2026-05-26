"use client"

import { useCallback, useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { api, UserItem } from "@/lib/api"
import { useAuth } from "@/lib/auth"
import { Loader2, Plus, Trash2 } from "lucide-react"
import { toast } from "sonner"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"

export default function UsersPage() {
  const { isOwner, loading: authLoading } = useAuth()
  const [users, setUsers] = useState<UserItem[]>([])
  const [loading, setLoading] = useState(true)
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [name, setName] = useState("")
  const [submitting, setSubmitting] = useState(false)

  const fetchUsers = useCallback(async () => {
    try {
      const data = await api.listUsers()
      setUsers(data)
    } catch {
      toast.error("Gagal memuat daftar pengguna")
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (isOwner) fetchUsers()
  }, [isOwner, fetchUsers])

  const handleCreate = async () => {
    if (!email.trim() || !password.trim()) return
    setSubmitting(true)
    try {
      await api.createUser({ email: email.trim(), password, name: name.trim() || undefined })
      toast.success("Editor berhasil ditambahkan")
      setEmail("")
      setPassword("")
      setName("")
      await fetchUsers()
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Gagal menambah pengguna")
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (id: string) => {
    try {
      await api.deleteUser(id)
      toast.success("Pengguna dihapus")
      await fetchUsers()
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Gagal menghapus")
    }
  }

  if (authLoading || loading) {
    return (
      <div className="flex items-center justify-center h-48">
        <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (!isOwner) {
    return <p className="text-muted-foreground">Hanya owner yang dapat mengakses halaman ini.</p>
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Kelola Pengguna</h1>
        <p className="text-muted-foreground">Tambah atau hapus akun editor</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <Plus className="w-4 h-4" /> Tambah Editor
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-4">
            <div className="space-y-1">
              <Label htmlFor="name">Nama</Label>
              <Input
                id="name"
                placeholder="Nama editor"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="editor@borneo.ai"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            <div className="flex items-end">
              <Button onClick={handleCreate} disabled={submitting || !email || !password}>
                {submitting && <Loader2 className="w-4 h-4 mr-1 animate-spin" />}
                Tambah
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Daftar Pengguna ({users.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {users.map((u) => (
              <div
                key={u.id}
                className="flex items-center justify-between rounded-lg border p-3"
              >
                <div className="flex items-center gap-3">
                  <div>
                    <p className="text-sm font-medium">{u.name || u.email}</p>
                    <p className="text-xs text-muted-foreground">{u.email}</p>
                  </div>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-primary/10 text-primary font-medium">
                    {u.role}
                  </span>
                  {!u.is_active && (
                    <span className="text-xs px-2 py-0.5 rounded-full bg-red-100 text-red-700">
                      nonaktif
                    </span>
                  )}
                </div>
                {u.role !== "owner" && (
                  <Dialog>
                    <DialogTrigger render={<Button variant="ghost" size="icon" className="text-red-500 hover:text-red-700" />}>
                      <Trash2 className="w-4 h-4" />
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Hapus Pengguna</DialogTitle>
                        <DialogDescription>
                          Yakin ingin menghapus {u.email}? Tindakan ini tidak dapat dibatalkan.
                        </DialogDescription>
                      </DialogHeader>
                      <DialogFooter>
                        <DialogClose render={<Button variant="outline" />}>Batal</DialogClose>
                        <Button variant="destructive" onClick={() => handleDelete(u.id)}>
                          Ya, Hapus
                        </Button>
                      </DialogFooter>
                    </DialogContent>
                  </Dialog>
                )}
              </div>
            ))}
            {users.length === 0 && (
              <p className="text-sm text-muted-foreground">Belum ada pengguna.</p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
