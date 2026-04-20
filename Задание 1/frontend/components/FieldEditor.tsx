"use client";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface FieldEditorProps {
  fieldKey: string;
  label: string;
  value: string;
  confidence: number;
  onChange: (value: string) => void;
  onFocus?: () => void;
}

function confidenceColor(c: number): string {
  if (c > 0.9) return "border-green-500";
  if (c >= 0.5) return "border-amber-500";
  return "border-red-500";
}

function confidencePercent(c: number): string {
  return `${Math.round(c * 100)}%`;
}

export default function FieldEditor({
  fieldKey,
  label,
  value,
  confidence,
  onChange,
  onFocus,
}: FieldEditorProps) {
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between">
        <Label htmlFor={fieldKey}>{label}</Label>
        <span
          className={`text-xs font-mono ${
            confidence > 0.9
              ? "text-green-600"
              : confidence >= 0.5
              ? "text-amber-600"
              : "text-red-600"
          }`}
        >
          {confidencePercent(confidence)}
        </span>
      </div>
      <Input
        id={fieldKey}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onFocus={onFocus}
        className={`${confidenceColor(confidence)} border-2`}
      />
    </div>
  );
}
