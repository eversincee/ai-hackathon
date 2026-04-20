"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { Assembly } from "@/lib/types";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

export default function AssembliesPage() {
  const [assemblies, setAssemblies] = useState<Assembly[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.assemblies
      .list()
      .then(setAssemblies)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <main className="container mx-auto py-10 px-4 space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/" className="text-sm text-muted-foreground hover:underline">
            &larr; Главная
          </Link>
          <h1 className="text-2xl font-bold">Сборки</h1>
        </div>
        <Link href="/assemblies/new">
          <Button>Новая сборка</Button>
        </Link>
      </div>

      {loading ? (
        <p className="text-muted-foreground">Загрузка...</p>
      ) : assemblies.length === 0 ? (
        <p className="text-muted-foreground">Нет сборок</p>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Название</TableHead>
              <TableHead>Код проекта</TableHead>
              <TableHead>Заводской номер</TableHead>
              <TableHead>Позиций</TableHead>
              <TableHead>Создана</TableHead>
              <TableHead>Действия</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {assemblies.map((a) => (
              <TableRow key={a.id}>
                <TableCell className="font-medium">{a.name}</TableCell>
                <TableCell>{a.project_code || "—"}</TableCell>
                <TableCell>{a.factory_number || "—"}</TableCell>
                <TableCell>{a.items.length}</TableCell>
                <TableCell>
                  {new Date(a.created_at).toLocaleDateString("ru-RU")}
                </TableCell>
                <TableCell>
                  <div className="flex gap-2">
                    <a
                      href={api.barcodes.assemblyLabelUrl(a.id)}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-primary underline"
                    >
                      Этикетка
                    </a>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </main>
  );
}
