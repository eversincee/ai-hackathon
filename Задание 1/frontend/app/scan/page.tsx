"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function ScanPage() {
  const router = useRouter();
  const [payload, setPayload] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleLookup(e: React.FormEvent) {
    e.preventDefault();
    if (!payload.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const result = await api.lookup(payload.trim());
      if (result.kind === "passport") {
        router.push(`/review/${result.id}`);
      } else if (result.kind === "assembly") {
        router.push(`/assemblies`);
      } else {
        setError(`Неизвестный тип: ${result.kind}`);
      }
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="container mx-auto py-10 px-4 space-y-6 max-w-lg">
      <div className="flex items-center gap-4">
        <Link href="/" className="text-sm text-muted-foreground hover:underline">
          &larr; Главная
        </Link>
        <h1 className="text-2xl font-bold">Сканирование штрихкода</h1>
      </div>

      <form onSubmit={handleLookup} className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="barcode">Содержимое штрихкода</Label>
          <Input
            id="barcode"
            value={payload}
            onChange={(e) => setPayload(e.target.value)}
            placeholder="Введите или отсканируйте штрихкод"
            autoFocus
          />
        </div>
        <Button type="submit" disabled={loading || !payload.trim()}>
          {loading ? "Поиск..." : "Найти"}
        </Button>
      </form>

      {error && (
        <div className="p-3 border border-red-300 rounded bg-red-50 text-red-700 text-sm">
          {error}
        </div>
      )}
    </main>
  );
}
