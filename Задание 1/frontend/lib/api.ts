import type { Passport, Assembly, ReceiptLine, AssemblyItem } from "./types";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API}${path}`, init);
  if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
  return res.json();
}

export const api = {
  passports: {
    ingest: async (file: File) => {
      const form = new FormData();
      form.append("file", file);
      return request<Passport[]>("/passports/ingest", { method: "POST", body: form });
    },
    list: (status?: string) =>
      request<Passport[]>(`/passports${status ? `?status=${status}` : ""}`),
    get: (id: string) => request<Passport>(`/passports/${id}`),
    patch: (id: string, updates: Partial<Passport>) =>
      request<Passport>(`/passports/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updates),
      }),
    approve: (id: string) =>
      request<Passport>(`/passports/${id}/approve`, { method: "POST" }),
  },
  assemblies: {
    list: () => request<Assembly[]>("/assemblies"),
    get: (id: string) => request<Assembly>(`/assemblies/${id}`),
    create: (body: {
      name: string;
      kind?: string | null;
      project_code?: string | null;
      factory_number?: string | null;
      items: AssemblyItem[];
    }) =>
      request<Assembly>("/assemblies", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      }),
    delete: (id: string) =>
      request<void>(`/assemblies/${id}`, { method: "DELETE" }),
  },
  receipts: {
    list: () => request<ReceiptLine[]>("/receipts"),
    importCsv: async (file: File) => {
      const form = new FormData();
      form.append("file", file);
      return request<{ imported: number }>("/receipts/import", {
        method: "POST",
        body: form,
      });
    },
  },
  lookup: (payload: string) =>
    request<{ kind: string; id: string }>(`/lookup/${payload}`),
  barcodes: {
    passportLabelUrl: (id: string) => `${API}/barcodes/passport/${id}/label.pdf`,
    assemblyLabelUrl: (id: string) => `${API}/barcodes/assembly/${id}/label.pdf`,
  },
  export: {
    csvUrl: () => `${API}/export/csv`,
    xmlUrl: () => `${API}/export/xml`,
    checklistUrl: () => `${API}/export/checklist.pdf`,
  },
};
