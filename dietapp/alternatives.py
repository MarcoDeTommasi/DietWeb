from __future__ import annotations

import math
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping
from typing import Any

from dietapp.domain import UNITS, normalise_food_name


NUTRIENT_FIELDS = ("calories", "carbohydrates", "protein", "fats")


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    return str(value).strip()


def _optional_non_negative(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        number = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError from error
    if math.isnan(number):
        return None
    if not math.isfinite(number) or number < 0:
        raise ValueError
    return number


def validate_alternative_rows(
    rows: Iterable[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[str]]:
    """Normalise user input and return clean records plus validation errors."""
    cleaned: list[dict[str, Any]] = []
    errors: list[str] = []

    for index, row in enumerate(rows, start=1):
        group_name = _clean_text(row.get("group_name"))
        food_name = normalise_food_name(_clean_text(row.get("food_name")))
        if not group_name and not food_name:
            continue
        location = f"Riga {index}"
        if not group_name:
            errors.append(f"{location}: gruppo mancante.")
        if not food_name:
            errors.append(f"{location}: alimento mancante.")

        try:
            quantity = float(row.get("quantity"))
            if not math.isfinite(quantity) or quantity <= 0:
                raise ValueError
        except (TypeError, ValueError):
            errors.append(f"{location}: quantità non valida.")
            quantity = 0.0

        unit = _clean_text(row.get("unit"))
        if unit not in UNITS:
            errors.append(f"{location}: unità non valida.")

        nutrients: dict[str, float | None] = {}
        for field in NUTRIENT_FIELDS:
            try:
                nutrients[field] = _optional_non_negative(row.get(field))
            except ValueError:
                errors.append(f"{location}: valore {field} non valido.")
                nutrients[field] = None

        notes = _clean_text(row.get("notes"))[:255] or None
        cleaned.append(
            {
                "group_name": group_name[:100],
                "food_name": food_name[:120],
                "quantity": quantity,
                "unit": unit,
                **nutrients,
                "notes": notes,
            }
        )

    canonical_groups: dict[str, str] = {}
    for row in cleaned:
        group_key = row["group_name"].casefold()
        row["group_name"] = canonical_groups.setdefault(
            group_key, row["group_name"]
        )

    duplicates = Counter(
        (row["group_name"].casefold(), row["food_name"]) for row in cleaned
    )
    for (group, food), count in duplicates.items():
        if count > 1:
            errors.append(f"Duplicato nel gruppo {group}: {food}.")

    group_sizes = Counter(row["group_name"].casefold() for row in cleaned)
    for group, count in group_sizes.items():
        if count < 2:
            errors.append(
                f"Il gruppo {group} deve contenere almeno due alimenti equivalenti."
            )
    return cleaned, errors


def group_alternatives(
    rows: Iterable[Mapping[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    grouped: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["group_name"])].append(dict(row))
    return dict(grouped)


def alternative_coverage(
    meal: Mapping[str, Any], rows: Iterable[Mapping[str, Any]]
) -> dict[str, Any]:
    """Report which meal foods can be substituted using complete groups."""
    grouped = group_alternatives(rows)
    covered: set[str] = set()
    groups_by_food: defaultdict[str, list[str]] = defaultdict(list)
    for group_name, items in grouped.items():
        if len(items) < 2:
            continue
        for item in items:
            groups_by_food[str(item["food_name"])].append(group_name)

    meal_foods = set(meal)
    for food in meal_foods:
        if groups_by_food.get(food):
            covered.add(food)
    missing = sorted(meal_foods - covered)
    return {
        "covered": sorted(covered),
        "missing": missing,
        "covered_count": len(covered),
        "total_count": len(meal_foods),
        "complete": bool(meal_foods) and not missing,
    }
