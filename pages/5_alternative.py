from __future__ import annotations

import logging

import pandas as pd
import streamlit as st

from dietapp.alternatives import alternative_coverage, validate_alternative_rows
from dietapp.database import session_scope
from dietapp.domain import readable_food_name
from dietapp.repositories import (
    RepositoryError,
    get_food_alternatives,
    get_user_diet,
    replace_food_alternatives,
)
from dietapp.ui import render_sidebar, require_authentication


LOGGER = logging.getLogger(__name__)

COLUMN_TO_FIELD = {
    "Gruppo equivalenza": "group_name",
    "Alimento": "food_name",
    "Quantità": "quantity",
    "Unità": "unit",
    "kcal": "calories",
    "Carboidrati (g)": "carbohydrates",
    "Proteine (g)": "protein",
    "Grassi (g)": "fats",
    "Note": "notes",
}


def editor_frame(alternatives: list[dict]) -> pd.DataFrame:
    rows = [
        {
            "Gruppo equivalenza": row["group_name"],
            "Alimento": readable_food_name(row["food_name"]),
            "Quantità": row["quantity"],
            "Unità": row["unit"],
            "kcal": row["calories"],
            "Carboidrati (g)": row["carbohydrates"],
            "Proteine (g)": row["protein"],
            "Grassi (g)": row["fats"],
            "Note": row["notes"],
        }
        for row in alternatives
    ]
    if not rows:
        rows = [
            {
                "Gruppo equivalenza": "",
                "Alimento": "",
                "Quantità": None,
                "Unità": "g",
                "kcal": None,
                "Carboidrati (g)": None,
                "Proteine (g)": None,
                "Grassi (g)": None,
                "Note": "",
            }
        ]
    return pd.DataFrame(rows, columns=COLUMN_TO_FIELD)


def plan_coverage(diet: dict | None, alternatives: list[dict]) -> tuple[int, int]:
    all_foods: dict[str, dict] = {}
    for meals in (diet or {}).values():
        if not isinstance(meals, dict):
            continue
        for foods in meals.values():
            if isinstance(foods, dict):
                all_foods.update(foods)
    report = alternative_coverage(all_foods, alternatives)
    return report["covered_count"], report["total_count"]


def plan_food_names(diet: dict | None) -> list[str]:
    foods: set[str] = set()
    for meals in (diet or {}).values():
        if not isinstance(meals, dict):
            continue
        for meal_foods in meals.values():
            if isinstance(meal_foods, dict):
                foods.update(meal_foods)
    return sorted(readable_food_name(food) for food in foods)


def main() -> None:
    st.set_page_config(
        page_title="Alternative alimentari · DietApp",
        page_icon="🔄",
        layout="wide",
    )
    if not require_authentication():
        st.stop()
    render_sidebar("Alternative alimentari")

    header, back = st.columns([8, 1])
    with header:
        st.title("🔄 Alternative alimentari")
    with back:
        if st.button("← Dashboard"):
            st.switch_page("pages/1_home.py")

    st.info(
        "Ogni gruppo descrive porzioni che consideri equivalenti. Inserisci almeno "
        "due alimenti per gruppo. Per collegare il gruppo a un pasto, almeno uno "
        "dei nomi deve coincidere con un alimento del piano. Fai verificare le "
        "equivalenze al professionista che ti segue, soprattutto in presenza di "
        "patologie o allergie."
    )
    with st.expander("Esempio di compilazione"):
        st.dataframe(
            pd.DataFrame(
                [
                    ["Carboidrati pranzo", "Pasta integrale", 80, "g"],
                    ["Carboidrati pranzo", "Pasta", 70, "g"],
                    ["Carboidrati pranzo", "Riso", 100, "g"],
                ],
                columns=["Gruppo", "Alimento", "Quantità", "Unità"],
            ),
            hide_index=True,
            width="stretch",
        )
        st.caption(
            "I numeri sono solo un esempio di struttura, non una prescrizione "
            "nutrizionale."
        )

    username = st.session_state["username"]
    try:
        with session_scope() as db:
            alternatives = get_food_alternatives(db, username)
            diet = get_user_diet(db, username)
    except RepositoryError:
        LOGGER.exception("Alternative loading failed")
        st.error("Non è stato possibile caricare le alternative.")
        return

    covered, total = plan_coverage(diet, alternatives)
    metric_1, metric_2, metric_3 = st.columns(3)
    metric_1.metric("Porzioni inserite", len(alternatives))
    metric_2.metric(
        "Gruppi",
        len({row["group_name"].casefold() for row in alternatives}),
    )
    metric_3.metric("Alimenti del piano coperti", f"{covered}/{total}")
    with st.expander("Nomi degli alimenti presenti nel piano"):
        st.write(", ".join(plan_food_names(diet)) or "Nessun alimento presente.")
        st.caption(
            "Usa questi nomi per collegare correttamente un gruppo di equivalenza "
            "agli alimenti del piano."
        )

    edited = st.data_editor(
        editor_frame(alternatives),
        num_rows="dynamic",
        hide_index=True,
        width="stretch",
        key="food_alternatives_editor",
        column_config={
            "Gruppo equivalenza": st.column_config.TextColumn(required=True),
            "Alimento": st.column_config.TextColumn(required=True),
            "Quantità": st.column_config.NumberColumn(
                min_value=0.01, step=1.0, required=True
            ),
            "Unità": st.column_config.SelectboxColumn(
                options=["g", "ml", "pz"], required=True
            ),
            "kcal": st.column_config.NumberColumn(min_value=0.0),
            "Carboidrati (g)": st.column_config.NumberColumn(min_value=0.0),
            "Proteine (g)": st.column_config.NumberColumn(min_value=0.0),
            "Grassi (g)": st.column_config.NumberColumn(min_value=0.0),
            "Note": st.column_config.TextColumn(),
        },
    )

    st.caption(
        "I valori nutrizionali si riferiscono alla porzione indicata. Sono "
        "opzionali, ma aumentano la precisione del confronto prodotto dal chatbot."
    )
    if st.button("Salva alternative", type="primary", width="stretch"):
        raw_rows = [
            {field: row[column] for column, field in COLUMN_TO_FIELD.items()}
            for row in edited.to_dict(orient="records")
        ]
        cleaned, errors = validate_alternative_rows(raw_rows)
        if errors:
            st.error("Correggi la tabella prima di salvare.")
            for error in errors:
                st.write(f"• {error}")
            return
        try:
            with session_scope() as db:
                saved = replace_food_alternatives(db, username, cleaned)
            if saved:
                st.success("Alternative alimentari salvate.")
                st.rerun()
            else:
                st.error("Utente non trovato. Effettua nuovamente il login.")
        except RepositoryError:
            LOGGER.exception("Alternative save failed")
            st.error("Salvataggio non riuscito. Le modifiche nell’editor restano visibili.")


if __name__ == "__main__":
    main()
