from pathlib import Path


TEMPLATE = Path("app/templates/admin/persons.html")


def test_person_page_shows_birth_date_and_edit_field():
    content = TEMPLATE.read_text(encoding="utf-8")
    assert "Nascimento" in content
    assert 'id="edit_birth_date"' in content
    assert 'id="new_birth_date"' in content


def test_excel_import_contains_birth_date():
    from app.utils.cadastro_import import read_cadastro_excel

    records = read_cadastro_excel(Path("docs/CadastroCoroinhas.xlsx"))
    assert records
    assert any(record["birth_date_serial"] for record in records)
