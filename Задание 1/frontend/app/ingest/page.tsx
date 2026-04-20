"use client";

import { useState } from "react";
import Link from "next/link";
import IngestDropZone from "@/components/IngestDropZone";
import type { Passport } from "@/lib/types";

export default function IngestPage() {
  const [created, setCreated] = useState<Passport[]>([]);

  function handleCreated(passports: Passport[]) {
    setCreated((prev) => [...prev, ...passports]);
  }

  return (
    <main className="container mx-auto py-10 px-4 space-y-8">
      <div className="flex items-center gap-4">
        <Link href="/" className="text-sm text-muted-foreground hover:underline">
          &larr; Главная
        </Link>
        <h1 className="text-2xl font-bold">Загрузка паспортов</h1>
      </div>

      <IngestDropZone onPassportsCreated={handleCreated} />

      {created.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-lg font-semibold">
            Созданные паспорта ({created.length})
          </h2>
          <div className="space-y-2">
            {created.map((p) => (
              <div
                key={p.id}
                className="flex items-center justify-between p-3 border rounded-lg"
              >
                <div>
                  <span className="font-medium">
                    {p.doc_number || "Без номера"}
                  </span>
                  <span className="text-sm text-muted-foreground ml-3">
                    {p.product_name}
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <span
                    className={`text-xs px-2 py-0.5 rounded ${
                      p.review_status === "needs_review"
                        ? "bg-amber-100 text-amber-700"
                        : "bg-green-100 text-green-700"
                    }`}
                  >
                    {p.review_status === "needs_review" ? "На ревью" : "Авто"}
                  </span>
                  <Link
                    href={`/review/${p.id}`}
                    className="text-sm text-primary underline"
                  >
                    Проверить
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </main>
  );
}
