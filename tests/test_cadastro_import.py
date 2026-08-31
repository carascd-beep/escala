from pathlib import Path

from app.utils.cadastro_import import (
    availability_label,
    experience_label,
    read_cadastro_excel,
)


EXCEL_PATH = Path(__file__).parents[1] / "docs" / "CadastroCoroinhas.xlsx"


def test_excel_cadastro_is_read_with_friendly_labels():
    records = read_cadastro_excel(EXCEL_PATH)

    assert len(records) == 47
    assert records[0]["full_name"] == "Arthur Santiago da Silva Nunes"
    assert records[0]["server_type"] == "acolito"
    assert records[0]["availability"] == "Fim de Semana"
    assert records[0]["experience"] == 3
    assert sum(record["server_type"] == "cerimoniario" for record in records) == 5


def test_cadastro_code_labels_are_explicit():
    assert availability_label("fs") == "Fim de Semana"
    assert availability_label("td") == "Todo Dia"
    assert experience_label(1) == "Baixa"
    assert experience_label(2) == "Média"
    assert experience_label(3) == "Alta"


def test_unknown_codes_are_safe_for_display():
    assert availability_label("x") == "x"
    assert experience_label(9) == "9"


def test_excel_path_must_exist():
    missing = EXCEL_PATH.with_name("missing.xlsx")

    try:
        read_cadastro_excel(missing)
    except FileNotFoundError as error:
        assert str(missing) in str(error)
    else:
        raise AssertionError("A importação deveria rejeitar um arquivo inexistente")
