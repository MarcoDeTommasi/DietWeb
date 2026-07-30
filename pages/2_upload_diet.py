from __future__ import annotations

import logging

import pandas as pd
import streamlit as st

from dietapp.database import session_scope
from dietapp.domain import (
    DAYS,
    MEALS,
    UNITS,
    conversion_dict,
    empty_diet,
    normalise_food_name,
    readable_food_name,
    validate_diet,
)
from dietapp.pdf_import import PdfImportError, get_food_list_from_pdf
from dietapp.repositories import RepositoryError, save_user_plan
from dietapp.ui import render_sidebar, require_authentication


LOGGER = logging.getLogger(__name__)


def initialise_editor() -> None:
    existing = st.session_state.get("dict_lunch")
    if not isinstance(existing, dict) or not existing:
        st.session_state["dict_lunch"] = empty_diet()
    else:
        complete = empty_diet()
        for day in DAYS:
            if isinstance(existing.get(day), dict):
                for meal in MEALS:
                    if isinstance(existing[day].get(meal), dict):
                        complete[day][meal] = existing[day][meal]
        st.session_state["dict_lunch"] = complete
    st.session_state.setdefault("food_list", [])
    st.session_state["current_day"] = min(
        max(int(st.session_state.get("current_day", 0)), 0), len(DAYS) - 1
    )


def render_pdf_import() -> None:
    with st.expander("Importa gli alimenti da PDF"):
        st.caption(
            "Il testo del PDF viene inviato al provider AI configurato per estrarre "
            "i nomi degli alimenti. Il file non viene salvato dall’app. Quantità e "
            "pasti restano sotto il tuo controllo."
        )
        uploaded = st.file_uploader(
            "Piano alimentare in PDF",
            type=["pdf"],
            accept_multiple_files=False,
        )
        if st.button("Estrai alimenti", disabled=uploaded is None):
            try:
                with st.spinner("Analisi del documento…"):
                    foods = get_food_list_from_pdf(uploaded.getvalue())
                if not foods:
                    st.warning("Nessun alimento riconosciuto.")
                else:
                    merged = sorted(set(st.session_state["food_list"]) | set(foods))
                    st.session_state["food_list"] = merged
                    st.success(f"Importati {len(foods)} alimenti.")
                    st.rerun()
            except PdfImportError as error:
                st.error(str(error))


def render_food_editor() -> None:
    st.subheader("1. Alimenti")
    current = [readable_food_name(food) for food in st.session_state["food_list"]]
    frame = pd.DataFrame({"Alimento": current or [""]})
    edited = st.data_editor(
        frame,
        num_rows="dynamic",
        hide_index=True,
        width="stretch",
        key="food_list_editor",
        column_config={"Alimento": st.column_config.TextColumn(required=True)},
    )
    if st.button("Applica lista alimenti"):
        raw_values = [
            str(value).strip()
            for value in edited["Alimento"].dropna().tolist()
            if str(value).strip()
        ]
        normalised = [normalise_food_name(value) for value in raw_values]
        if len(normalised) != len(set(normalised)):
            st.error("La lista contiene duplicati.")
        elif not normalised:
            st.error("Inserisci almeno un alimento.")
        else:
            st.session_state["food_list"] = normalised
            st.success("Lista aggiornata.")
            st.rerun()


def day_editor() -> tuple[str, dict[str, dict]]:
    day = DAYS[st.session_state["current_day"]]
    labels = conversion_dict(st.session_state["food_list"])
    reverse_labels = {label: code for code, label in labels.items()}
    st.subheader(f"2. Piano · {day}")
    edited_day: dict[str, dict] = {}
    columns = st.columns(2)

    for index, meal in enumerate(MEALS):
        with columns[index % 2]:
            st.markdown(f"**{meal}**")
            data = [
                [
                    labels.get(food, readable_food_name(food)),
                    details.get("Quantità", 0),
                    details.get("Unità", "g"),
                ]
                for food, details in st.session_state["dict_lunch"][day][meal].items()
            ]
            frame = pd.DataFrame(data, columns=["Alimento", "Quantità", "Unità"])
            edited = st.data_editor(
                frame,
                key=f"meal_editor_{day}_{meal}",
                hide_index=True,
                num_rows="dynamic",
                width="stretch",
                column_config={
                    "Alimento": st.column_config.SelectboxColumn(
                        options=list(labels.values()), required=True
                    ),
                    "Quantità": st.column_config.NumberColumn(
                        min_value=0.0, step=1.0, required=True
                    ),
                    "Unità": st.column_config.SelectboxColumn(
                        options=list(UNITS), required=True
                    ),
                },
            )
            meal_data: dict[str, dict] = {}
            for _, row in edited.iterrows():
                label = row.get("Alimento")
                if pd.isna(label) or not str(label).strip():
                    continue
                code = reverse_labels.get(str(label), normalise_food_name(str(label)))
                quantity = row.get("Quantità", 0)
                unit = row.get("Unità", "g")
                meal_data[code] = {
                    "Quantità": 0 if pd.isna(quantity) else quantity,
                    "Unità": "g" if pd.isna(unit) else unit,
                }
            edited_day[meal] = meal_data
    return day, edited_day


def apply_day(day: str, data: dict[str, dict]) -> None:
    st.session_state["dict_lunch"][day] = data


def main() -> None:
    st.set_page_config(
        page_title="Piano alimentare · DietApp", page_icon="✏️", layout="wide"
    )
    if not require_authentication():
        st.stop()
    render_sidebar("Piano alimentare")
    initialise_editor()

    header, back = st.columns([8, 1])
    with header:
        st.title("✏️ Piano alimentare")
    with back:
        if st.button("← Dashboard"):
            st.switch_page("pages/1_home.py")

    render_pdf_import()
    render_food_editor()
    if not st.session_state["food_list"]:
        st.info("Aggiungi almeno un alimento per compilare il piano.")
        return

    day, edited_day = day_editor()
    previous, progress, next_column = st.columns([1, 3, 1])
    with previous:
        if st.button(
            "← Precedente",
            disabled=st.session_state["current_day"] == 0,
            width="stretch",
        ):
            apply_day(day, edited_day)
            st.session_state["current_day"] -= 1
            st.rerun()
    with progress:
        st.progress(
            (st.session_state["current_day"] + 1) / len(DAYS),
            text=f"Giorno {st.session_state['current_day'] + 1} di {len(DAYS)}",
        )
    with next_column:
        if st.button(
            "Successivo →",
            disabled=st.session_state["current_day"] == len(DAYS) - 1,
            width="stretch",
        ):
            apply_day(day, edited_day)
            st.session_state["current_day"] += 1
            st.rerun()

    st.divider()
    if st.button("Salva piano", type="primary", width="stretch"):
        apply_day(day, edited_day)
        errors = validate_diet(
            st.session_state["dict_lunch"], st.session_state["food_list"]
        )
        if errors:
            st.error("Correggi i dati non validi prima di salvare.")
            with st.expander(f"Dettagli ({len(errors)})", expanded=True):
                for error in errors[:30]:
                    st.write(f"• {error}")
        else:
            try:
                with session_scope() as db:
                    saved = save_user_plan(
                        db,
                        st.session_state["username"],
                        st.session_state["dict_lunch"],
                        st.session_state["food_list"],
                    )
                if saved:
                    st.success("Piano salvato.")
                    st.switch_page("pages/1_home.py")
                else:
                    st.error("Utente non trovato. Effettua nuovamente il login.")
            except RepositoryError:
                LOGGER.exception("Diet save failed")
                st.error("Salvataggio non riuscito. I dati nell’editor non sono persi.")


if __name__ == "__main__":
    main()
