from __future__ import annotations

import logging
from datetime import datetime

import pandas as pd
import streamlit as st

from dietapp.database import session_scope
from dietapp.domain import ENGLISH_TO_ITALIAN_DAY, readable_food_name
from dietapp.meal_assistant import (
    MealAssistantError,
    alternatives_notice,
    assistant_context,
    generate_reply,
    initial_request,
)
from dietapp.repositories import (
    RepositoryError,
    get_food_alternatives,
    get_user_diet,
)
from dietapp.ui import render_sidebar, require_authentication


LOGGER = logging.getLogger(__name__)


def get_meal_selection(username: str) -> tuple[str, dict, list[dict]]:
    selected = st.session_state.get("meal_assistant_context", {})
    day = selected.get("day")
    with session_scope() as db:
        diet = get_user_diet(db, username) or {}
        alternatives = get_food_alternatives(db, username)
    if day not in diet:
        day = ENGLISH_TO_ITALIAN_DAY[datetime.now().strftime("%A")]
    meal = diet.get(day, {}).get("Pranzo", {})
    st.session_state["meal_assistant_context"] = {"day": day, "meal": meal}
    return day, meal, alternatives


def meal_frame(meal: dict) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Alimento": readable_food_name(food),
                "Quantità": details.get("Quantità"),
                "Unità": details.get("Unità"),
            }
            for food, details in meal.items()
        ]
    )


def ask_assistant(context: dict, request: str) -> None:
    messages = st.session_state.setdefault("meal_assistant_messages", [])
    messages.append({"role": "user", "content": request})
    try:
        with st.spinner("Sto preparando il suggerimento…"):
            reply = generate_reply(context, messages)
        messages.append({"role": "assistant", "content": reply})
    except MealAssistantError as error:
        LOGGER.exception("Meal assistant request failed")
        st.session_state["meal_assistant_error"] = str(error)


def main() -> None:
    st.set_page_config(
        page_title="Assistente del pranzo · DietApp",
        page_icon="💬",
        layout="wide",
    )
    if not require_authentication():
        st.stop()
    render_sidebar("Assistente del pranzo")

    header, actions = st.columns([6, 2])
    with header:
        st.title("💬 Assistente del pranzo")
        st.caption(
            "Preparazioni e sostituzioni condividono la stessa conversazione."
        )
    with actions:
        if st.button("← Dashboard", width="stretch"):
            st.switch_page("pages/1_home.py")
        if st.button("Cancella chat", width="stretch"):
            st.session_state["meal_assistant_messages"] = []
            st.session_state.pop("meal_assistant_error", None)
            st.rerun()

    try:
        day, meal, alternatives = get_meal_selection(st.session_state["username"])
    except RepositoryError:
        LOGGER.exception("Assistant context loading failed")
        st.error("Non è stato possibile caricare il pranzo e le alternative.")
        return

    if not meal:
        st.warning(f"Non ci sono alimenti nel pranzo di {day}.")
        return

    context = assistant_context(day, meal, alternatives)
    st.subheader(f"Pranzo di {day}")
    st.dataframe(meal_frame(meal), hide_index=True, width="stretch")
    notice = alternatives_notice(context)
    if notice:
        st.warning(notice)
    else:
        st.success("Le alternative coprono tutti gli alimenti di questo pranzo.")

    preparation, alternative, manage = st.columns([1, 1, 1])
    with preparation:
        if st.button("👩‍🍳 Genera preparazione", width="stretch"):
            st.session_state["meal_assistant_pending"] = "preparation"
            st.rerun()
    with alternative:
        if st.button("🔄 Genera pasto alternativo", width="stretch"):
            st.session_state["meal_assistant_pending"] = "alternative"
            st.rerun()
    with manage:
        if st.button("Gestisci alternative", width="stretch"):
            st.switch_page("pages/5_alternative.py")

    pending = st.session_state.pop("meal_assistant_pending", None)
    if pending:
        ask_assistant(context, initial_request(pending))

    error = st.session_state.pop("meal_assistant_error", None)
    if error:
        st.error(error)

    st.divider()
    for message in st.session_state.setdefault("meal_assistant_messages", []):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_message = st.chat_input(
        "Chiedi una variante, chiarisci un passaggio o modifica la preparazione…",
        max_chars=2_000,
    )
    if user_message:
        ask_assistant(context, user_message)
        st.rerun()

    st.caption(
        "I suggerimenti sono generati automaticamente e non sostituiscono il "
        "parere del nutrizionista o del medico."
    )


if __name__ == "__main__":
    main()
