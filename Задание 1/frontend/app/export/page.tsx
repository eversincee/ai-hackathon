"use client";

import Link from "next/link";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function ExportPage() {
  return (
    <main className="container mx-auto py-10 px-4 space-y-6 max-w-2xl">
      <div className="flex items-center gap-4">
        <Link href="/" className="text-sm text-muted-foreground hover:underline">
          &larr; Главная
        </Link>
        <h1 className="text-2xl font-bold">Экспорт данных</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">CSV для 1С</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Выгрузка данных паспортов в формате CSV
            </p>
            <a href={api.export.csvUrl()} target="_blank" rel="noopener noreferrer">
              <Button className="w-full">Скачать CSV</Button>
            </a>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">CommerceML XML</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Выгрузка в формате CommerceML
            </p>
            <a href={api.export.xmlUrl()} target="_blank" rel="noopener noreferrer">
              <Button className="w-full">Скачать XML</Button>
            </a>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Чек-лист PDF</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Печатный чек-лист для проверки
            </p>
            <a
              href={api.export.checklistUrl()}
              target="_blank"
              rel="noopener noreferrer"
            >
              <Button className="w-full">Скачать PDF</Button>
            </a>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}
