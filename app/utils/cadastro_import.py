"""Leitura segura do cadastro inicial exportado em Excel."""
from pathlib import Path
from typing import Any
from unicodedata import normalize
from zipfile import ZipFile
from xml.etree import ElementTree

NAMESPACE = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
AVAILABILITY_LABELS = {"fs": "Fim de Semana", "td": "Todo Dia"}
EXPERIENCE_LABELS = {1: "Baixa", 2: "Média", 3: "Alta"}
SERVER_TYPE_LABELS = {"coroinha": "Coroinha", "acolito": "Acólito", "cerimoniario": "Cerimoniário"}


def _shared_strings(book: ZipFile) -> list[str]:
    root = ElementTree.fromstring(book.read("xl/sharedStrings.xml"))
    return ["".join(node.itertext()) for node in root.findall("main:si", NAMESPACE)]


def availability_label(value: str) -> str:
    return AVAILABILITY_LABELS.get(value.strip().lower(), value)


def experience_label(value: int) -> str:
    return EXPERIENCE_LABELS.get(value, str(value))


def read_cadastro_excel(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(source)
    with ZipFile(source) as book:
        strings = _shared_strings(book)
        sheet = ElementTree.fromstring(book.read("xl/worksheets/sheet1.xml"))
        rows = []
        for row in sheet.findall(".//main:row", NAMESPACE):
            values = []
            for cell in row.findall("main:c", NAMESPACE):
                value = cell.find("main:v", NAMESPACE)
                text = value.text if value is not None and value.text else ""
                if cell.get("t") == "s":
                    text = strings[int(text)]
                values.append(text.strip())
            rows.append(values)
    records = []
    for full_name, birth_date, function, availability, experience in rows[1:]:
        server_type = "".join(
            char for char in normalize("NFD", function.strip().lower())
            if char not in "\u0300\u0301"
        )
        level = int(experience)
        records.append({
            "full_name": full_name,
            "birth_date_serial": birth_date,
            "server_type": server_type,
            "server_type_label": SERVER_TYPE_LABELS.get(server_type, function.strip()),
            "availability": availability_label(availability),
            "experience": level,
            "experience_label": experience_label(level),
        })
    return records