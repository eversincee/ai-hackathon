"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import type { Passport } from "@/lib/types";
import ReviewPanel from "@/components/ReviewPanel";

export default function ReviewPage() {
  const params = useParams<{ id: string }>();
  const [passport, setPassport] = useState<Passport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [focusedField, setFocusedField] = useState<string | null>(null);

  useEffect(() => {
    if (!params.id) return;
    api.passports
      .get(params.id)
      .then(setPassport)
      .catch((err) => setError(String(err)))
      .finally(() => setLoading(false));
  }, [params.id]);

  if (loading) {
    return (
      <main className="container mx-auto py-10 px-4">
        <p>Загрузка...</p>
      </main>
    );
  }

  if (error || !passport) {
    return (
      <main className="container mx-auto py-10 px-4">
        <p className="text-red-600">Ошибка: {error || "Паспорт не найден"}</p>
        <Link href="/" className="text-sm text-primary underline mt-4 inline-block">
          На главную
        </Link>
      </main>
    );
  }

  const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const scanFilename = passport.source_scan_path?.split(/[\\/]/).pop() ?? "";
  const scanUrl = scanFilename ? `${API}/scans/${encodeURIComponent(scanFilename)}` : null;
  const isPdf = scanFilename.toLowerCase().endsWith(".pdf");

  return (
    <main className="container mx-auto py-10 px-4">
      <div className="flex items-center gap-4 mb-6">
        <Link href="/" className="text-sm text-muted-foreground hover:underline">
          &larr; Главная
        </Link>
        <h1 className="text-2xl font-bold">
          Ревью: {passport.doc_number || passport.id.slice(0, 8)}
        </h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: scan image */}
        <div className="border rounded-lg p-4 bg-muted/30">
          <h3 className="text-sm font-medium mb-3">Скан документа</h3>
          {scanUrl ? (
            <div className="space-y-2">
              {isPdf ? (
                <iframe
                  src={scanUrl}
                  title="Скан паспорта"
                  className="w-full h-[75vh] rounded border bg-white"
                />
              ) : (
                /* eslint-disable-next-line @next/next/no-img-element */
                <img
                  src={scanUrl}
                  alt="Скан паспорта"
                  className="max-w-full rounded border"
                  onError={(e) => {
                    (e.target as HTMLImageElement).style.display = "none";
                  }}
                />
              )}
              <a
                href={scanUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-primary underline"
              >
                Открыть оригинал
              </a>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">Скан не доступен</p>
          )}
          {focusedField && (
            <p className="text-xs text-muted-foreground mt-2">
              Выбранное поле: {focusedField}
            </p>
          )}
        </div>

        {/* Right: review panel */}
        <ReviewPanel
          passport={passport}
          onUpdate={setPassport}
          onBboxFocus={setFocusedField}
        />
      </div>
    </main>
  );
}
