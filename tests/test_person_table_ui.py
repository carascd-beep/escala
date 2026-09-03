from pathlib import Path

from app.schemas.person import PersonCreate


TEMPLATE = Path("app/templates/admin/persons.html")


def test_person_page_uses_single_sortable_table_with_status_and_edit():
    content = TEMPLATE.read_text(encoding="utf-8")
    assert content.count("id=\"personsTable\"") == 1
    assert "data-sort-key=\"display_name\"" in content
    assert "data-sort-key=\"birth_date\"" in content
    assert "data-sort-key=\"is_active\"" in content
    assert "onclick=\"editPerson({{ person.id }})\"" in content
    assert "id=\"edit_is_active\"" in content
    assert "name=\"fixed_weekdays\"" not in content
    assert "id=\"edit_fixed_weekdays\"" not in content
    assert "bothExperienceSummary" in content
    assert "both_experience_counts.get(0, 0)" in content


def test_availability_aliases_are_stored_canonically():
    base = {
        "full_name": "Pessoa Teste",
        "display_name": "Pessoa",
        "server_type": "coroinha",
    }
    assert PersonCreate(**base, availability="Todo Dia").availability == "ambos"
    assert PersonCreate(**base, availability="Ambos").availability == "ambos"
    assert PersonCreate(**base, availability="Semana").availability == "semana"
    assert PersonCreate(**base, availability="Fim de Semana").availability == "fim de semana"
