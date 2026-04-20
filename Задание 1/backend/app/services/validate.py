import re
from dataclasses import dataclass, field

from app.services.vendors import find_vendor_by_doc_number

DOC_NUMBER_RE = re.compile(r"^[A-ZА-Я]{3,5}\.\d{6}\.\d{3}[- ]?\d?\s*ПС$")


@dataclass
class ValidationResult:
    is_valid: bool
    errors: dict[str, str] = field(default_factory=dict)


def _value(field_dict):
    if not field_dict:
        return None
    return field_dict.get("value") if isinstance(field_dict, dict) else field_dict


def _as_int_safe(value):
    if value in (None, "", []):
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    try:
        return int(float(str(value).split()[0]))
    except (ValueError, TypeError, IndexError):
        return None


def validate_passport_data(data: dict) -> ValidationResult:
    errors: dict[str, str] = {}

    doc_number = _value(data.get("doc_number"))
    if not isinstance(doc_number, str) or not DOC_NUMBER_RE.match(doc_number):
        errors["doc_number"] = f"unrecognized doc number format: {doc_number!r}"

    serials_raw = _value(data.get("serial_numbers")) or []
    serials = [s for s in serials_raw if isinstance(s, str)] if isinstance(serials_raw, list) else []
    if isinstance(doc_number, str) and doc_number.startswith("TREI.") and serials:
        trei_pat = re.compile(r"^[A-Z]\d[A-Z]\d{4}$")
        bad = [s for s in serials if not trei_pat.match(s)]
        if bad:
            errors["serial_numbers"] = f"TREI serials should match pattern: {bad}"

    if isinstance(doc_number, str) and doc_number.startswith("БНРД.") and serials:
        tecon_pat = re.compile(r"^\d{7}$")
        bad = [s for s in serials if not tecon_pat.match(s)]
        if bad:
            errors["serial_numbers"] = f"БНРД serials should be 7 digits: {bad}"

    warranty = _as_int_safe(_value(data.get("warranty_months")))
    issue_date = _value(data.get("issue_date"))
    if warranty and warranty > 0 and not issue_date:
        errors["issue_date"] = "warranty > 0 requires issue_date"

    manufacturer = _value(data.get("manufacturer_name"))
    if isinstance(doc_number, str) and isinstance(manufacturer, str):
        vendor = find_vendor_by_doc_number(doc_number)
        if vendor and manufacturer != vendor["name"]:
            errors["manufacturer_name"] = (
                f"doc_number prefix implies {vendor['name']!r}, got {manufacturer!r}"
            )

    return ValidationResult(is_valid=not errors, errors=errors)
