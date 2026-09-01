"""Motor parametrizável para geração de escalas."""
from collections import Counter
from dataclasses import dataclass, field
from datetime import date
from typing import Iterable, Mapping, Sequence

from app.models.person import Person

_WEEKEND = {5, 6}
_DEFAULT_FUNCTION_PRIORITY = ("coroinha", "acolito", "cerimoniario")


@dataclass(frozen=True)
class ScheduleParameters:
    scope: str = "all"
    participants_per_scale: int = 2
    priority_experience: tuple[int, ...] = (3, 2, 1, 0)
    priority_server_types: tuple[str, ...] = field(default_factory=tuple)
    participants_by_server_type: dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
        if self.scope not in {"all", "weekday", "weekend"}:
            raise ValueError("Escopo deve ser all, weekday ou weekend")
        if self.participants_per_scale < 1:
            raise ValueError("A quantidade de participantes deve ser positiva")


def _availability_matches(person: Person, mass_date: date) -> bool:
    value = (person.availability or "").strip().lower().replace("-", " ")
    weekend = mass_date.weekday() in _WEEKEND
    if value in {"ambos", "todo dia", "todos", "semana e fim de semana"}:
        return True
    if value in {"fim de semana", "fim semana", "fds", "fs"}:
        return weekend
    if value in {"semana", "dia de semana", "dias de semana", "td"}:
        return not weekend
    return False


def _scope_matches(scope: str, mass_date: date) -> bool:
    return scope == "all" or (scope == "weekend") == (mass_date.weekday() in _WEEKEND)


def _fixed_matches(person: Person, mass: Mapping[str, object]) -> bool:
    ids = getattr(person, "fixed_schedule_ids", [])
    return not ids or mass.get("schedule_id") in ids


def _fixed_weekday_matches(person: Person, mass_date: date) -> bool:
    raw = getattr(person, "fixed_weekdays", None) or ""
    fixed = {int(value) for value in str(raw).split(",") if value.strip().isdigit()}
    return not fixed or mass_date.weekday() in fixed


def generate_assignments(
    people: Sequence[Person],
    masses: Iterable[Mapping[str, object]],
    parameters: ScheduleParameters | None = None,
) -> dict[int, tuple[Person, ...]]:
    """Gera equipes, expandindo vagas para cobrir disponíveis."""
    params = parameters or ScheduleParameters()
    active = [p for p in people if p.is_active and p.experience in (0, 1, 2, 3)]
    selected = [m for m in masses if _scope_matches(params.scope, m["date"])]
    assignments: dict[int, tuple[Person, ...]] = {}
    usage: Counter[int] = Counter()
    function_priority = params.priority_server_types or _DEFAULT_FUNCTION_PRIORITY

    for mass in sorted(selected, key=lambda item: item["date"]):
        eligible = [p for p in active if _availability_matches(p, mass["date"]) and _fixed_matches(p, mass)]
        if len(eligible) < params.participants_per_scale or not any(p.experience == 3 for p in eligible):
            raise ValueError(f"não foi possível formar equipe válida para a missa {mass['id']}")

        def key(person: Person):
            type_rank = function_priority.index(person.server_type.value) if person.server_type.value in function_priority else len(function_priority)
            fixed_rank = 0 if getattr(person, "fixed_weekdays", None) and _fixed_weekday_matches(person, mass["date"]) else 1
            experience_rank = params.priority_experience.index(person.experience) if person.experience in params.priority_experience else len(params.priority_experience)
            return (type_rank, fixed_rank, usage[person.id or id(person)], experience_rank, person.display_name)

        if params.participants_by_server_type:
            required = params.participants_by_server_type
            if sum(required.values()) != params.participants_per_scale:
                raise ValueError("A soma das quantidades por função deve ser igual ao total")
            chosen = []
            for server_type, quantity in required.items():
                candidates = sorted((p for p in eligible if p.server_type.value == server_type), key=key)
                if len(candidates) < quantity:
                    raise ValueError(f"não foi possível atender a quantidade da função {server_type}")
                chosen.extend(candidates[:quantity])
        else:
            chosen = sorted(eligible, key=key)[:params.participants_per_scale]

        if not any(p.experience == 3 for p in chosen):
            high = min((p for p in eligible if p.experience == 3), key=key)
            high_index = next((i for i, p in enumerate(chosen) if p.server_type == high.server_type), None)
            if high_index is None:
                high_index = len(chosen) - 1
            chosen[high_index] = high

        if any(p.experience == 0 for p in chosen):
            extras = [p for p in sorted(eligible, key=key) if p not in chosen]
            chosen.extend(extras[:max(0, 3 - len(chosen))])
            if len(chosen) < 3:
                raise ValueError("não foi possível formar equipe de no mínimo 3 pessoas")

        assignments[int(mass["id"])] = tuple(chosen)
        for person in chosen:
            usage[person.id or id(person)] += 1

    missing = [p for p in active if usage[p.id or id(p)] == 0 and any(_availability_matches(p, m["date"]) for m in selected)]
    if missing:
        for person in missing:
            candidates = [(mass_id, next(m for m in selected if int(m["id"]) == mass_id)) for mass_id in assignments]
            candidates = [item for item in candidates if _availability_matches(person, item[1]["date"]) and _fixed_matches(person, item[1])]
            if not candidates:
                raise ValueError(f"não foi possível escalar todos os disponíveis: {person.display_name}")
            mass_id, mass = min(candidates, key=lambda item: (0 if _fixed_weekday_matches(person, item[1]["date"]) else 1, len(assignments[item[0]]), item[1]["date"]))
            assignments[mass_id] = tuple(list(assignments[mass_id]) + [person])
            usage[person.id or id(person)] += 1

    return assignments


def generate_assignments_legacy(people, masses):
    return generate_assignments(people, masses)


# Compatibilidade explícita com o chamador antigo.
def generate_assignments_legacy(people, masses):
    return generate_assignments(people, masses)
