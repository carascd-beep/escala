from pathlib import Path


TEMPLATE = Path("app/templates/admin/persons.html")


def test_person_page_has_edit_modal_and_handler():
    content = TEMPLATE.read_text(encoding="utf-8")
    assert 'id="editPersonModal"' in content
    assert "async function editPerson(id)" in content
    assert "PUT", "/api/pessoas/" in content
