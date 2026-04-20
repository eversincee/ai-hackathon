"use client";

import Link from "next/link";
import AssemblyBuilder from "@/components/AssemblyBuilder";

export default function NewAssemblyPage() {
  return (
    <main className="container mx-auto py-10 px-4 space-y-6">
      <div className="flex items-center gap-4">
        <Link
          href="/assemblies"
          className="text-sm text-muted-foreground hover:underline"
        >
          &larr; Сборки
        </Link>
        <h1 className="text-2xl font-bold">Новая сборка</h1>
      </div>

      <AssemblyBuilder />
    </main>
  );
}
