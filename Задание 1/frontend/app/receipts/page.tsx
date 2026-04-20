"use client";

import { useEffect, useState, useRef } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { ReceiptLine } from "@/lib/types";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

export default function ReceiptsPage() {
  const [receipts, setReceipts] = useState<ReceiptLine[]>([]);
  const [loading, setLoading] = useState(true);
  const [importing, setImporting] = useState(false);
  const [importResult, setImportResult] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadReceipts();
  }, []);

  function loadReceipts() {
    setLoading(true);
    api.receipts
      .list()
      .then(setReceipts)
      .catch(() => {})
      .finally(() => setLoading(false));
  }

  async function handleImport(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setImporting(true);
    setImportResult(null);
    try {
      const result = await api.receipts.importCsv(file);
      setImportResult(`Импортировано строк: ${result.imported}`);
      loadReceipts();
    } catch (err) {
      setImportResult(`Ошибка: ${err}`);
    } finally {
      setImporting(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  }

  return (
    <main className="container mx-auto py-10 px-4 space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/" className="text-sm text-muted-foreground hover:underline">
          &larr; Главная
        </Link>
        <h1 className="text-2xl font-bold">Приходные накладные</h1>
      </div>

      <div className="flex items-center gap-4">
        <div>
          <input
            ref={fileRef}
            type="file"
            accept=".csv"
            onChange={handleImport}
            className="hidden"
            id="csv-upload"
          />
          <Button
            onClick={() => fileRef.current?.click()}
            disabled={importing}
          >
            {importing ? "Импорт..." : "Импорт CSV"}
          </Button>
        </div>
        {importResult && (
          <span className="text-sm text-muted-foreground">{importResult}</span>
        )}
      </div>

      {loading ? (
        <p className="text-muted-foreground">Загрузка...</p>
      ) : receipts.length === 0 ? (
        <p className="text-muted-foreground">Нет данных</p>
      ) : (
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Документ</TableHead>
                <TableHead>Дата</TableHead>
                <TableHead>Код позиции</TableHead>
                <TableHead>Номенклатура</TableHead>
                <TableHead>Ед. изм.</TableHead>
                <TableHead>Цена</TableHead>
                <TableHead>Кол-во заявл.</TableHead>
                <TableHead>Кол-во факт.</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {receipts.map((r) => (
                <TableRow key={r.id}>
                  <TableCell className="font-medium">
                    {r.receipt_doc_number}
                  </TableCell>
                  <TableCell>{r.receipt_date}</TableCell>
                  <TableCell>{r.position_code}</TableCell>
                  <TableCell className="max-w-[200px] truncate">
                    {r.nomenclature}
                  </TableCell>
                  <TableCell>{r.unit}</TableCell>
                  <TableCell>{r.price}</TableCell>
                  <TableCell>{r.qty_declared}</TableCell>
                  <TableCell>{r.qty_actual}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </main>
  );
}
