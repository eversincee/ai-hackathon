from app.models.passport import DocType


def classify_doc_type(merged: dict) -> DocType:
    serials_field = merged.get("serial_numbers", {})
    serials = serials_field.get("value") if isinstance(serials_field, dict) else serials_field
    if not serials:
        return DocType.no_serial
    if len(serials) >= 2:
        return DocType.group
    return DocType.single
