"use client";

import { useState } from "react";
import type { Passport } from "@/lib/types";
import { api } from "@/lib/api";
import FieldEditor from "./FieldEditor";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface ReviewPanelProps {
  passport: Passport;
  onUpdate: (p: Passport) => void;
  onBboxFocus?: (fieldKey: string) => void;
}

export default function ReviewPanel({ passport, onUpdate, onBboxFocus }: ReviewPanelProps) {
  const [draft, setDraft] = useState<Partial<Passport>>({});
  const [serials, setSerials] = useState<string[]>(passport.serial_numbers);
  const [saving, setSaving] = useState(false);
  const [approving, setApproving] = useState(false);

  const merged = { ...passport, ...draft };

  function setField(key: string, value: string) {
    setDraft((prev) => ({ ...prev, [key]: value }));
  }

  const fields: { key: string; label: string }[] = [
    { key: "doc_number", label: "Номер документа" },
    { key: "product_name", label: "Наименование изделия" },
    { key: "product_code", label: "Код продукции" },
    { key: "manufacturer_name", label: "Производитель" },
    { key: "manufacturer_address", label: "Адрес производителя" },
    { key: "issue_date", label: "Дата выпуска" },
  ];

  async function handleSave() {
    setSaving(true);
    try {
      const updates = { ...draft, serial_numbers: serials };
      const updated = await api.passports.patch(passport.id, updates);
      onUpdate(updated);
      setDraft({});
    } catch (err) {
      alert(`Ошибка сохранения: ${err}`);
    } finally {
      setSaving(false);
    }
  }

  async function handleApprove() {
    setApproving(true);
    try {
      const updated = await api.passports.approve(passport.id);
      onUpdate(updated);
    } catch (err) {
      alert(`Ошибка: ${err}`);
    } finally {
      setApproving(false);
    }
  }

  function addSerial() {
    setSerials((prev) => [...prev, ""]);
  }

  function removeSerial(index: number) {
    setSerials((prev) => prev.filter((_, i) => i !== index));
  }

  function updateSerial(index: number, value: string) {
    setSerials((prev) => prev.map((s, i) => (i === index ? value : s)));
  }

  return (
    <div className="space-y-4 overflow-y-auto max-h-[85vh] pr-2">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold">Проверка паспорта</h2>
        <span
          className={`px-2 py-1 rounded text-xs font-medium ${
            passport.review_status === "approved"
              ? "bg-green-100 text-green-700"
              : passport.review_status === "needs_review"
              ? "bg-amber-100 text-amber-700"
              : "bg-blue-100 text-blue-700"
          }`}
        >
          {passport.review_status === "approved"
            ? "Одобрен"
            : passport.review_status === "needs_review"
            ? "На ревью"
            : "Авто"}
        </span>
      </div>

      <div className="text-xs text-muted-foreground">
        Общая уверенность: {Math.round(passport.extraction_confidence * 100)}%
      </div>

      {fields.map((f) => (
        <FieldEditor
          key={f.key}
          fieldKey={f.key}
          label={f.label}
          value={String((merged as Record<string, unknown>)[f.key] ?? "")}
          confidence={passport.field_confidences[f.key] ?? 0}
          onChange={(v) => setField(f.key, v)}
          onFocus={() => onBboxFocus?.(f.key)}
        />
      ))}

      {/* Serial numbers */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <Label>Серийные номера</Label>
          <Button variant="outline" size="sm" onClick={addSerial}>
            + Добавить
          </Button>
        </div>
        {serials.map((s, i) => (
          <div key={i} className="flex gap-2">
            <Input
              value={s}
              onChange={(e) => updateSerial(i, e.target.value)}
              placeholder={`Серийный номер ${i + 1}`}
            />
            <Button variant="ghost" size="sm" onClick={() => removeSerial(i)}>
              &times;
            </Button>
          </div>
        ))}
        {serials.length === 0 && (
          <p className="text-xs text-muted-foreground">Нет серийных номеров</p>
        )}
      </div>

      {/* Tech specs (read-only display) */}
      {Object.keys(passport.tech_specs).length > 0 && (
        <div className="space-y-1">
          <Label>Технические характеристики</Label>
          <div className="text-sm space-y-1 bg-muted/50 rounded p-3">
            {Object.entries(passport.tech_specs).map(([k, v]) => (
              <div key={k} className="flex justify-between">
                <span className="text-muted-foreground">{k}</span>
                <span>{v}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Stamps & signatures */}
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <Label>Печати</Label>
          <p className="text-muted-foreground">
            {passport.stamps_detected.length > 0
              ? passport.stamps_detected.join(", ")
              : "Не обнаружены"}
          </p>
        </div>
        <div>
          <Label>Подписи</Label>
          <p className="text-muted-foreground">
            {passport.signatures_detected.length > 0
              ? passport.signatures_detected.join(", ")
              : "Не обнаружены"}
          </p>
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-3 pt-4 border-t">
        <Button onClick={handleSave} disabled={saving}>
          {saving ? "Сохранение..." : "Сохранить"}
        </Button>
        <Button
          onClick={handleApprove}
          disabled={approving || passport.review_status === "approved"}
          variant="outline"
          className="border-green-500 text-green-600 hover:bg-green-50"
        >
          {approving ? "..." : "Одобрить"}
        </Button>
        <a
          href={api.barcodes.passportLabelUrl(passport.id)}
          target="_blank"
          rel="noopener noreferrer"
        >
          <Button variant="outline" size="sm">
            Скачать этикетку
          </Button>
        </a>
      </div>
    </div>
  );
}
