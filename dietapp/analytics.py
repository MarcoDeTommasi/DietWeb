from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

import pandas as pd

from dietapp.domain import readable_food_name, storage_food_name


COLUMNS = ["Acquisto", "Data", "Alimento", "Quantità", "Unità"]


def purchases_to_frame(records: Iterable[Mapping[str, Any]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for record in records:
        date = pd.to_datetime(record.get("data"), errors="coerce")
        shopping = record.get("lista_spesa", {})
        if pd.isna(date) or not isinstance(shopping, Mapping):
            continue
        for food_key, details in shopping.items():
            if not isinstance(details, Mapping):
                continue
            quantity = pd.to_numeric(details.get("Quantità"), errors="coerce")
            unit = details.get("Unità")
            if pd.isna(quantity) or unit not in {"g", "ml", "pz"}:
                continue
            food = storage_food_name(str(food_key))
            rows.append(
                {
                    "Acquisto": record.get("id"),
                    "Data": date,
                    "Alimento": food,
                    "Quantità": float(quantity),
                    "Unità": unit,
                    "Alimento leggibile": readable_food_name(food),
                }
            )
    if not rows:
        return pd.DataFrame(columns=COLUMNS + ["Alimento leggibile"])
    return pd.DataFrame(rows)


def filter_period(frame: pd.DataFrame, months: int | None, now=None) -> pd.DataFrame:
    if months is None or frame.empty:
        return frame.copy()
    reference = pd.Timestamp(now) if now is not None else pd.Timestamp.now()
    threshold = reference.normalize() - pd.DateOffset(months=months)
    return frame.loc[frame["Data"] >= threshold].copy()
