"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import Link from "next/link";
import { api } from "@/lib/api";
import type { Passport } from "@/lib/types";
import { Button } from "@/components/ui/button";

interface FileStatus {
  name: string;
  status: "pending" | "processing" | "done" | "error";
  error?: string;
  passports?: Passport[];
}

interface IngestDropZoneProps {
  onPassportsCreated?: (passports: Passport[]) => void;
}

export default function IngestDropZone({ onPassportsCreated }: IngestDropZoneProps) {
  const [files, setFiles] = useState<FileStatus[]>([]);

  const processFiles = useCallback(
    async (acceptedFiles: File[]) => {
      const initial: FileStatus[] = acceptedFiles.map((f) => ({
        name: f.name,
        status: "pending" as const,
      }));
      setFiles((prev) => [...prev, ...initial]);

      for (let i = 0; i < acceptedFiles.length; i++) {
        const file = acceptedFiles[i];
        setFiles((prev) =>
          prev.map((f) =>
            f.name === file.name && f.status === "pending"
              ? { ...f, status: "processing" }
              : f
          )
        );

        try {
          const passports = await api.passports.ingest(file);
          setFiles((prev) =>
            prev.map((f) =>
              f.name === file.name && f.status === "processing"
                ? { ...f, status: "done", passports }
                : f
            )
          );
          onPassportsCreated?.(passports);
        } catch (err) {
          setFiles((prev) =>
            prev.map((f) =>
              f.name === file.name && f.status === "processing"
                ? { ...f, status: "error", error: String(err) }
                : f
            )
          );
        }
      }
    },
    [onPassportsCreated]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: processFiles,
    accept: {
      "application/pdf": [".pdf"],
      "image/*": [".png", ".jpg", ".jpeg", ".tiff", ".tif"],
    },
  });

  return (
    <div className="space-y-4">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors ${
          isDragActive ? "border-primary bg-primary/5" : "border-muted-foreground/30 hover:border-primary/50"
        }`}
      >
        <input {...getInputProps()} />
        {isDragActive ? (
          <p className="text-lg">Перетащите файлы сюда...</p>
        ) : (
          <div>
            <p className="text-lg mb-2">Перетащите сканы паспортов сюда</p>
            <p className="text-sm text-muted-foreground">
              PDF, PNG, JPG, TIFF
            </p>
            <Button variant="outline" className="mt-4">
              Выбрать файлы
            </Button>
          </div>
        )}
      </div>

      {files.length > 0 && (
        <div className="space-y-2">
          <h3 className="font-medium">Загруженные файлы</h3>
          {files.map((f, idx) => (
            <div
              key={`${f.name}-${idx}`}
              className="flex items-center justify-between p-3 border rounded-lg"
            >
              <div className="flex items-center gap-3">
                <span className="text-sm font-medium">{f.name}</span>
                {f.status === "pending" && (
                  <span className="text-xs text-muted-foreground">В очереди</span>
                )}
                {f.status === "processing" && (
                  <span className="text-xs text-blue-600">Обработка...</span>
                )}
                {f.status === "done" && (
                  <span className="text-xs text-green-600">Готово</span>
                )}
                {f.status === "error" && (
                  <span className="text-xs text-red-600" title={f.error}>
                    Ошибка
                  </span>
                )}
              </div>
              {f.status === "done" && f.passports && (
                <div className="flex gap-2">
                  {f.passports.map((p) => (
                    <Link
                      key={p.id}
                      href={`/review/${p.id}`}
                      className="text-xs text-primary underline"
                    >
                      {p.doc_number || p.id.slice(0, 8)}
                    </Link>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
