from __future__ import annotations

import math
import re
import unicodedata
from collections import defaultdict
from collections.abc import Iterable, Mapping
from decimal import Decimal, InvalidOperation
from typing import Any


DAYS = [
    "Lunedì",
    "Martedì",
    "Mercoledì",
    "Giovedì",
    "Venerdì",
    "Sabato",
    "Domenica",
]
MEALS = [
    "Colazione",
    "Pranzo",
    "Cena",
    "Spuntino Mattina",
    "Spuntino Pomeriggio",
]
UNITS = ("g", "ml", "pz")
ENGLISH_TO_ITALIAN_DAY = {
    "Monday": "Lunedì",
    "Tuesday": "Martedì",
    "Wednesday": "Mercoledì",
    "Thursday": "Giovedì",
    "Friday": "Venerdì",
    "Saturday": "Sabato",
    "Sunday": "Domenica",
}

EMOJI_MAP = {
    "latte": "🥛",
    "yogurt": "🥣",
    "ricotta": "🧀",
    "pane": "🍞",
    "fette_biscottate": "🍞",
    "pasta": "🍝",
    "farro": "🌾",
    "cous_cous": "🍚",
    "biscotti": "🍪",
    "piadina": "🌮",
    "patate": "🥔",
    "cereali": "🥣",
    "pollo": "🍗",
    "fesa": "🍗",
    "prosciutto": "🥓",
    "uova": "🥚",
    "filetto": "🥩",
    "carne": "🥩",
    "tonno": "🐟",
    "pesce": "🐟",
    "merluzzo": "🐟",
    "salmone": "🐟",
    "frutta": "🍎",
    "frutto": "🍎",
    "mandorle": "🥜",
    "marmellata": "🍯",
    "verdura": "🥦",
    "ortaggi": "🥕",
    "pomodori": "🍅",
    "fagioli": "🫘",
}


def empty_diet() -> dict[str, dict[str, dict[str, Any]]]:
    return {day: {meal: {} for meal in MEALS} for day in DAYS}


def normalise_food_name(value: str) -> str:
    text = unicodedata.normalize("NFKD", str(value).strip())
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r"[^a-zA-Z0-9]+", "_", text.lower())
    return text.strip("_")


def storage_food_name(value: str) -> str:
    """Remove the internal unit suffix used only for name/unit collisions."""
    return value.rsplit("::", 1)[0]


def readable_food_name(value: str) -> str:
    return storage_food_name(value).replace("_", " ").strip().title()


def get_food_emoji(food_name: str) -> str:
    normalised = normalise_food_name(storage_food_name(food_name))
    for key, emoji in EMOJI_MAP.items():
        if key in normalised:
            return emoji
    return "🥗"


def conversion_dict(food_list: Iterable[str]) -> dict[str, str]:
    return {food: readable_food_name(food) for food in food_list}


def _as_positive_number(value: Any) -> int | float:
    if isinstance(value, bool):
        raise ValueError
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as error:
        raise ValueError from error
    if not number.is_finite() or number <= 0:
        raise ValueError
    return int(number) if number == number.to_integral() else float(number)


def validate_diet(
    diet: Mapping[str, Any], allowed_foods: Iterable[str] | None = None
) -> list[str]:
    errors: list[str] = []
    if not isinstance(diet, Mapping):
        return ["Il piano alimentare non è un dizionario valido."]
    allowed = set(allowed_foods) if allowed_foods is not None else None
    food_count = 0

    for day in DAYS:
        meals = diet.get(day)
        if not isinstance(meals, Mapping):
            errors.append(f"{day}: giornata mancante o non valida.")
            continue
        for meal in MEALS:
            foods = meals.get(meal)
            if not isinstance(foods, Mapping):
                errors.append(f"{day} · {meal}: pasto mancante o non valido.")
                continue
            for food, details in foods.items():
                food_count += 1
                location = f"{day} · {meal} · {food or 'alimento senza nome'}"
                if not str(food).strip() or not isinstance(details, Mapping):
                    errors.append(f"{location}: alimento non valido.")
                    continue
                if allowed is not None and food not in allowed:
                    errors.append(
                        f"{location}: alimento assente dalla lista principale."
                    )
                try:
                    _as_positive_number(details.get("Quantità"))
                except ValueError:
                    errors.append(f"{location}: quantità non valida.")
                if details.get("Unità") not in UNITS:
                    errors.append(f"{location}: unità non valida.")
    if food_count == 0:
        errors.append("Inserisci almeno un alimento nel piano settimanale.")
    return errors


RequirementKey = tuple[str, str]
Requirements = dict[RequirementKey, int | float]


def aggregate_requirements(
    diet: Mapping[str, Any], selected_days: Iterable[str]
) -> Requirements:
    totals: defaultdict[RequirementKey, Decimal] = defaultdict(Decimal)
    selected = list(dict.fromkeys(selected_days))
    if not selected:
        raise ValueError("Seleziona almeno un giorno.")

    for day in selected:
        meals = diet.get(day)
        if not isinstance(meals, Mapping):
            raise ValueError(f"Il giorno {day} non è presente nella dieta.")
        for meal in MEALS:
            foods = meals.get(meal, {})
            if not isinstance(foods, Mapping):
                raise ValueError(f"Il pasto {meal} di {day} non è valido.")
            for food, details in foods.items():
                try:
                    quantity = Decimal(str(details["Quantità"]))
                    unit = str(details["Unità"])
                except (KeyError, TypeError, InvalidOperation) as error:
                    raise ValueError(
                        f"Dato non valido per {food} ({day}, {meal})."
                    ) from error
                if not quantity.is_finite() or quantity <= 0 or unit not in UNITS:
                    raise ValueError(f"Quantità o unità non valida per {food}.")
                totals[(str(food), unit)] += quantity

    result: Requirements = {}
    for key, value in totals.items():
        result[key] = int(value) if value == value.to_integral() else float(value)
    return result


def build_shopping_list(
    requirements: Mapping[RequirementKey, int | float],
    inventory: Mapping[RequirementKey, int | float],
) -> dict[str, dict[str, int | float | str]]:
    unit_count: defaultdict[str, int] = defaultdict(int)
    for food, _unit in requirements:
        unit_count[food] += 1

    shopping: dict[str, dict[str, int | float | str]] = {}
    for (food, unit), required in requirements.items():
        available = inventory.get((food, unit), 0)
        remaining = max(0, required - available)
        if math.isclose(float(remaining), 0.0):
            continue
        key = food if unit_count[food] == 1 else f"{food}::{unit}"
        shopping[key] = {"Quantità": remaining, "Unità": unit}
    return shopping
