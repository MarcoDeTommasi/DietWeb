from __future__ import annotations

import logging
from datetime import datetime

import streamlit as st

from dietapp.database import session_scope
from dietapp.domain import (
    DAYS,
    ENGLISH_TO_ITALIAN_DAY,
    conversion_dict,
    get_food_emoji,
)
from dietapp.repositories import (
    RepositoryError,
    get_user_diet,
    get_user_food_list,
    get_user_name,
    get_user_purchases,
    update_password,
)
from dietapp.security import validate_password
from dietapp.ui import render_sidebar, require_authentication


LOGGER = logging.getLogger(__name__)


def current_meal(hour: int | None = None) -> str:
    hour = datetime.now().hour if hour is None else hour
    if hour < 11:
        return "Colazione"
    if hour < 16:
        return "Pranzo"
    return "Cena"


def render_meals(
    diet: dict,
    day: str,
    selected_meals: list[str],
    food_list: list[str],
) -> None:
    labels = conversion_dict(food_list)
    day_plan = diet.get(day, {})
    main_column, snacks_column = st.columns(2)

    with main_column:
        st.subheader("Pasti principali")
        for meal in selected_meals:
            foods = day_plan.get(meal, {})
            st.markdown(f"**{meal}**")
            if not foods:
                st.caption("Nessun alimento inserito.")
            for food, details in foods.items():
                name = labels.get(food, food.replace("_", " ").title())
                st.write(
                    f"{get_food_emoji(food)} {name}: "
                    f"{details.get('Quantità', '–')} {details.get('Unità', '')}"
                )
            if meal == "Pranzo" and foods:
                preparation, alternative = st.columns(2)
                with preparation:
                    if st.button(
                        "👩‍🍳 Come lo preparo?",
                        key=f"prepare_{day}",
                        width="stretch",
                    ):
                        st.session_state["meal_assistant_context"] = {
                            "day": day,
                            "meal": foods,
                        }
                        st.session_state["meal_assistant_pending"] = "preparation"
                        st.switch_page("pages/6_assistente.py")
                with alternative:
                    if st.button(
                        "🔄 Pasto alternativo",
                        key=f"alternative_{day}",
                        width="stretch",
                    ):
                        st.session_state["meal_assistant_context"] = {
                            "day": day,
                            "meal": foods,
                        }
                        st.session_state["meal_assistant_pending"] = "alternative"
                        st.switch_page("pages/6_assistente.py")

    with snacks_column:
        st.subheader("Spuntini")
        for meal in ("Spuntino Mattina", "Spuntino Pomeriggio"):
            foods = day_plan.get(meal, {})
            st.markdown(f"**{meal}**")
            if not foods:
                st.caption("Nessun alimento inserito.")
            for food, details in foods.items():
                name = labels.get(food, food.replace("_", " ").title())
                st.write(
                    f"{get_food_emoji(food)} {name}: "
                    f"{details.get('Quantità', '–')} {details.get('Unità', '')}"
                )


def load_dashboard_data(username: str):
    with session_scope() as db:
        name = get_user_name(db, username)
        diet = get_user_diet(db, username)
        foods = get_user_food_list(db, username)
        purchase_count = len(get_user_purchases(db, username))
    return name, diet, foods, purchase_count


def password_form(username: str) -> None:
    with st.expander("🔒 Sicurezza account"):
        with st.form("change_password_form"):
            current = st.text_input("Password attuale", type="password")
            new = st.text_input("Nuova password", type="password")
            confirmation = st.text_input("Conferma nuova password", type="password")
            submitted = st.form_submit_button("Aggiorna password")
        if submitted:
            error = validate_password(new)
            if error:
                st.error(error)
            elif new != confirmation:
                st.error("Le nuove password non corrispondono.")
            else:
                try:
                    with session_scope() as db:
                        updated = update_password(db, username, current, new)
                    if updated:
                        st.success("Password aggiornata.")
                    else:
                        st.error("La password attuale non è corretta.")
                except RepositoryError:
                    LOGGER.exception("Password update failed")
                    st.error("Aggiornamento non riuscito. Riprova.")


def main() -> None:
    st.set_page_config(page_title="Dashboard · DietApp", page_icon="🍽️", layout="wide")
    if not require_authentication():
        st.stop()

    username = st.session_state["username"]
    try:
        (first_name, last_name), diet, food_list, purchase_count = (
            load_dashboard_data(username)
        )
    except RepositoryError:
        LOGGER.exception("Dashboard data loading failed")
        st.error("Non è stato possibile caricare i tuoi dati.")
        st.stop()

    st.session_state["nome"] = first_name
    st.session_state["cognome"] = last_name
    render_sidebar("Dashboard")

    st.title(f"🍽️ Ciao {first_name or username}")
    st.caption("Gestisci il piano alimentare e prepara la prossima spesa.")
    password_form(username)

    if not diet or not food_list:
        st.info("Inizia creando la lista degli alimenti e il tuo piano settimanale.")
        if st.button("Crea il piano", type="primary"):
            st.session_state["dict_lunch"] = diet or {}
            st.session_state["food_list"] = food_list or []
            st.switch_page("pages/2_upload_diet.py")
        return

    st.session_state["dict_lunch"] = diet
    st.session_state["food_list"] = food_list

    action_1, action_2, action_3, action_4 = st.columns(4)
    with action_1:
        st.subheader("🛒 Lista della spesa")
        st.caption("Calcola cosa comprare in base a ciò che hai già.")
        if st.button("Apri generatore", width="stretch", type="primary"):
            st.switch_page("pages/3_lista_spesa.py")
    with action_2:
        st.subheader("📊 Analisi")
        st.caption(f"{purchase_count} liste salvate nello storico.")
        if st.button(
            "Apri analisi",
            width="stretch",
            disabled=purchase_count == 0,
        ):
            st.switch_page("pages/4_analytics.py")
    with action_3:
        st.subheader("✏️ Piano alimentare")
        st.caption("Aggiorna alimenti, quantità e unità.")
        if st.button("Modifica piano", width="stretch"):
            st.session_state["current_day"] = 0
            st.switch_page("pages/2_upload_diet.py")
    with action_4:
        st.subheader("🔄 Alternative")
        st.caption("Definisci porzioni equivalenti per il chatbot.")
        if st.button("Gestisci alternative", width="stretch"):
            st.switch_page("pages/5_alternative.py")

    st.divider()
    st.subheader("Il piano del giorno")
    current_day = ENGLISH_TO_ITALIAN_DAY[datetime.now().strftime("%A")]
    selector, meal_selector = st.columns([1, 2])
    with selector:
        day = st.selectbox("Giorno", DAYS, index=DAYS.index(current_day))
    with meal_selector:
        meal = st.multiselect(
            "Pasti da mostrare",
            ["Colazione", "Pranzo", "Cena"],
            default=[current_meal()],
        )
    render_meals(diet, day, meal, food_list)


if __name__ == "__main__":
    main()
