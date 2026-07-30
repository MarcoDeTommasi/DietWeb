from __future__ import annotations

import hashlib
import json
import logging
from datetime import date

import pandas as pd
import streamlit as st

from dietapp.database import session_scope
from dietapp.domain import (
    DAYS,
    aggregate_requirements,
    build_shopping_list,
    get_food_emoji,
    readable_food_name,
    storage_food_name,
)
from dietapp.repositories import RepositoryError, save_purchase
from dietapp.ui import render_sidebar, require_authentication


LOGGER = logging.getLogger(__name__)


def payload_signature(value: dict) -> str:
    encoded = json.dumps(value, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def render_inventory_form(requirements):
    inventory = {}
    with st.form("inventory_form"):
        st.subheader("2. Indica cosa hai già in dispensa")
        st.caption("Lascia zero per gli alimenti che non hai.")
        columns = st.columns(2)
        for index, ((food, unit), required) in enumerate(requirements.items()):
            with columns[index % 2]:
                available = st.number_input(
                    f"{get_food_emoji(food)} {readable_food_name(food)} · "
                    f"necessari {required:g} {unit}",
                    min_value=0.0,
                    max_value=float(required),
                    value=0.0,
                    step=1.0,
                    key=f"inventory_{food}_{unit}",
                )
                inventory[(food, unit)] = available
        submitted = st.form_submit_button(
            "Genera lista", type="primary", width="stretch"
        )
    return submitted, inventory


def render_shopping_list(shopping: dict) -> None:
    st.subheader("3. Lista della spesa")
    if not shopping:
        st.success("Hai già tutto il necessario per i giorni selezionati.")
        return

    frame = pd.DataFrame(
        [
            {
                "Acquistato": False,
                "Alimento": f"{get_food_emoji(food)} {readable_food_name(food)}",
                "Quantità": details["Quantità"],
                "Unità": details["Unità"],
            }
            for key, details in shopping.items()
            for food in [storage_food_name(key)]
        ]
    )
    checked = st.data_editor(
        frame,
        hide_index=True,
        width="stretch",
        key=f"shopping_editor_{payload_signature(shopping)[:12]}",
        disabled=["Alimento", "Quantità", "Unità"],
        column_config={
            "Acquistato": st.column_config.CheckboxColumn("Preso"),
            "Quantità": st.column_config.NumberColumn(format="%.1f"),
        },
    )
    if not checked.empty and checked["Acquistato"].all():
        st.success("Tutti gli alimenti sono stati acquistati.")

    signature = payload_signature(shopping)
    already_saved = st.session_state.get("saved_shopping_signature") == signature
    if st.button(
        "Salva nello storico",
        disabled=already_saved,
        width="stretch",
    ):
        try:
            with session_scope() as db:
                saved = save_purchase(
                    db,
                    st.session_state["username"],
                    date.today().isoformat(),
                    shopping,
                )
            if saved:
                st.session_state["saved_shopping_signature"] = signature
                st.success("Lista salvata nello storico.")
                st.rerun()
            else:
                st.error("Utente non trovato. Effettua nuovamente il login.")
        except RepositoryError:
            LOGGER.exception("Purchase save failed")
            st.error("Salvataggio non riuscito. Riprova.")
    elif already_saved:
        st.caption("Questa lista è già stata salvata nello storico.")


def main() -> None:
    st.set_page_config(
        page_title="Lista della spesa · DietApp", page_icon="🛒", layout="wide"
    )
    if not require_authentication():
        st.stop()
    render_sidebar("Lista della spesa")

    header, back = st.columns([8, 1])
    with header:
        st.title("🛒 Lista della spesa")
    with back:
        if st.button("← Dashboard"):
            st.switch_page("pages/1_home.py")

    diet = st.session_state.get("dict_lunch")
    if not isinstance(diet, dict) or not diet:
        st.error("Il piano alimentare non è disponibile.")
        return

    st.subheader("1. Scegli i giorni")
    selected_days = st.multiselect(
        "Giorni", DAYS, placeholder="Seleziona uno o più giorni"
    )
    if not selected_days:
        st.info("Seleziona almeno un giorno per iniziare.")
        return

    context = "|".join(selected_days)
    if st.session_state.get("shopping_context") != context:
        st.session_state.pop("shopping_list", None)
        st.session_state["shopping_context"] = context

    try:
        requirements = aggregate_requirements(diet, selected_days)
    except ValueError as error:
        st.error(str(error))
        return

    submitted, inventory = render_inventory_form(requirements)
    if submitted:
        st.session_state["shopping_list"] = build_shopping_list(
            requirements, inventory
        )
    if "shopping_list" in st.session_state:
        render_shopping_list(st.session_state["shopping_list"])


if __name__ == "__main__":
    main()
