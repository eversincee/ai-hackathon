export type DocType = "single" | "group" | "no_serial";
export type ReviewStatus = "auto" | "needs_review" | "approved";

export interface Passport {
  id: string;
  source_scan_path: string;
  source_bboxes: Record<string, number[]>;
  doc_number: string;
  doc_type: DocType;
  product_name: string;
  product_code: string | null;
  manufacturer_name: string | null;
  manufacturer_address: string | null;
  issue_date: string | null;
  serial_numbers: string[];
  tech_specs: Record<string, string>;
  warranty_months: number | null;
  service_life_years: number | null;
  stamps_detected: string[];
  signatures_detected: string[];
  extraction_confidence: number;
  field_confidences: Record<string, number>;
  review_status: ReviewStatus;
  barcode_payload: string;
  created_at: string;
  reviewed_at: string | null;
}

export interface AssemblyItem {
  position: number;
  document_name: string;
  passport_id: string | null;
  factory_number: string | null;
  pages_count: string | null;
  has_certificate: boolean;
}

export interface Assembly {
  id: string;
  name: string;
  kind: string | null;
  project_code: string | null;
  factory_number: string | null;
  items: AssemblyItem[];
  barcode_payload: string;
  created_at: string;
}

export interface ReceiptLine {
  id: string;
  receipt_doc_number: string;
  receipt_date: string;
  position_code: string;
  nomenclature: string;
  type_brand: string | null;
  nomenclature_code_su: string | null;
  unit: string;
  price: string;
  qty_declared: number;
  qty_actual: number;
  linked_passport_ids: string[];
}
