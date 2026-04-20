"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import type { Passport, AssemblyItem } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function AssemblyBuilder() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [projectCode, setProjectCode] = useState("");
  const [factoryNumber, setFactoryNumber] = useState("");
  const [passports, setPassports] = useState<Passport[]>([]);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.passports
      .list()
      .then(setPassports)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  function togglePassport(id: string) {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  async function handleSave() {
    if (!name.trim()) {
      alert("Введите название сборки");
      return;
    }
    setSaving(true);
    try {
      const items: AssemblyItem[] = Array.from(selected).map((id, index) => {
        const p = passports.find((pp) => pp.id === id);
        return {
          position: index + 1,
          document_name: p?.product_name ?? "",
          passport_id: id,
          factory_number: p?.serial_numbers[0] ?? null,
          pages_count: null,
          has_certificate: false,
        };
      });
      await api.assemblies.create({
        name,
        project_code: projectCode || null,
        factory_number: factoryNumber || null,
        items,
      });
      router.push("/assemblies");
    } catch (err) {
      alert(`Ошибка: ${err}`);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="space-y-1">
          <Label htmlFor="name">Название сборки *</Label>
          <Input
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Комплект ИД"
          />
        </div>
        <div className="space-y-1">
          <Label htmlFor="project_code">Код проекта</Label>
          <Input
            id="project_code"
            value={projectCode}
            onChange={(e) => setProjectCode(e.target.value)}
          />
        </div>
        <div className="space-y-1">
          <Label htmlFor="factory_number">Заводской номер</Label>
          <Input
            id="factory_number"
            value={factoryNumber}
            onChange={(e) => setFactoryNumber(e.target.value)}
          />
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">
            Выберите паспорта ({selected.size} выбрано)
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p className="text-sm text-muted-foreground">Загрузка...</p>
          ) : passports.length === 0 ? (
            <p className="text-sm text-muted-foreground">Нет доступных паспортов</p>
          ) : (
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {passports.map((p) => (
                <label
                  key={p.id}
                  className="flex items-center gap-3 p-2 rounded hover:bg-muted/50 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={selected.has(p.id)}
                    onChange={() => togglePassport(p.id)}
                    className="rounded"
                  />
                  <div className="flex-1 min-w-0">
                    <span className="text-sm font-medium">
                      {p.doc_number || "Без номера"}
                    </span>
                    <span className="text-xs text-muted-foreground ml-2">
                      {p.product_name}
                    </span>
                  </div>
                  <span
                    className={`text-xs px-1.5 py-0.5 rounded ${
                      p.review_status === "approved"
                        ? "bg-green-100 text-green-700"
                        : p.review_status === "needs_review"
                        ? "bg-amber-100 text-amber-700"
                        : "bg-blue-100 text-blue-700"
                    }`}
                  >
                    {p.review_status}
                  </span>
                </label>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Button onClick={handleSave} disabled={saving || !name.trim()}>
        {saving ? "Создание..." : "Создать сборку"}
      </Button>
    </div>
  );
}
