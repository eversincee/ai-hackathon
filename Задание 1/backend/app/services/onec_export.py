import csv
import io
import xml.etree.ElementTree as ET
from xml.dom import minidom
from app.models.passport import Passport

CSV_COLUMNS = [
    "N", "Код позиции", "Номенклатура", "Характеристики номенклатуры",
    "Представление номенклатуры", "Код номенклатуры СУ",
    "Единица измерения", "Цена", "Количество заявленное", "Количество в т.ч. перегруз",
]

def passports_to_csv(passports: list[Passport]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(CSV_COLUMNS)
    for i, p in enumerate(passports, start=1):
        writer.writerow([
            i,
            p.product_code or "",
            p.product_name or "",
            "",
            p.product_name or "",
            p.doc_number or "",
            "шт",
            "",
            len(p.serial_numbers) if p.serial_numbers else 1,
            len(p.serial_numbers) if p.serial_numbers else 1,
        ])
    return buf.getvalue()

def passports_to_commerceml_xml(passports: list[Passport]) -> str:
    root = ET.Element("КоммерческаяИнформация", ВерсияСхемы="2.10")
    catalog = ET.SubElement(root, "Каталог")
    items = ET.SubElement(catalog, "Товары")

    for p in passports:
        item = ET.SubElement(items, "Товар")
        ET.SubElement(item, "Ид").text = p.id
        ET.SubElement(item, "Наименование").text = p.product_name or ""

        requisites = ET.SubElement(item, "ЗначенияРеквизитов")

        def add_requisite(name: str, value: str):
            r = ET.SubElement(requisites, "ЗначениеРеквизита")
            ET.SubElement(r, "Наименование").text = name
            ET.SubElement(r, "Значение").text = value

        add_requisite("Номер документа", p.doc_number or "")
        add_requisite("Код заказа", p.product_code or "")
        add_requisite("Производитель", p.manufacturer_name or "")
        add_requisite("Штрихкод", p.barcode_payload)
        for s in p.serial_numbers or []:
            add_requisite("Заводской номер", s)

    rough = ET.tostring(root, encoding="unicode")
    return minidom.parseString(rough).toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")
