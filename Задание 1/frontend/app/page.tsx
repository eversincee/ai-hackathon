"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { Passport } from "@/lib/types";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

export default function Dashboard() {
  const [passports, setPassports] = useState<Passport[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.passports
      .list()
      .then(setPassports)
      .catch(() => setPassports([]))
      .finally(() => setLoading(false));
  }, []);

  const total = passports.length;
  const needsReview = passports.filter((p) => p.review_status === "needs_review").length;
  const approved = passports.filter(
    (p) => p.review_status === "approved" || p.review_status === "auto"
  ).length;

  return (
    <main className="container mx-auto py-10 px-4 space-y-8">
      <h1 className="text-3xl font-bold">Оцифровка паспортов</h1>

      {/* Navigation cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Link href="/ingest">
          <Card className="hover:bg-muted/50 transition-colors cursor-pointer h-full">
            <CardHeader>
              <CardTitle>Загрузить паспорта</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Загрузка сканов для распознавания
              </p>
            </CardContent>
          </Card>
        </Link>
        <Link href="/assemblies">
          <Card className="hover:bg-muted/50 transition-colors cursor-pointer h-full">
            <CardHeader>
              <CardTitle>Сборки</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Управление комплектами документов
              </p>
            </CardContent>
          </Card>
        </Link>
        <Link href="/receipts">
          <Card className="hover:bg-muted/50 transition-colors cursor-pointer h-full">
            <CardHeader>
              <CardTitle>Импорт 1С</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Импорт приходных накладных из CSV
              </p>
            </CardContent>
          </Card>
        </Link>
      </div>

      {/* Counter cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm text-muted-foreground">Всего паспортов</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold">{loading ? "..." : total}</p>
          </CardContent>
        </Card>
        <Card className="border-amber-300">
          <CardHeader>
            <CardTitle className="text-sm text-amber-600">На ревью</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold text-amber-600">
              {loading ? "..." : needsReview}
            </p>
          </CardContent>
        </Card>
        <Card className="border-green-300">
          <CardHeader>
            <CardTitle className="text-sm text-green-600">Одобрено</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold text-green-600">
              {loading ? "..." : approved}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Bottom links */}
      <div className="flex gap-4">
        <Link href="/scan">
          <Card className="hover:bg-muted/50 transition-colors cursor-pointer px-6 py-4">
            <span className="font-medium">Сканировать штрихкод</span>
          </Card>
        </Link>
        <Link href="/export">
          <Card className="hover:bg-muted/50 transition-colors cursor-pointer px-6 py-4">
            <span className="font-medium">Экспорт</span>
          </Card>
        </Link>
      </div>
    </main>
  );
}
