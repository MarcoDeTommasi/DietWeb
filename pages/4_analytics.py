from __future__ import annotations

import logging

import plotly.express as px
import streamlit as st

from dietapp.analytics import filter_period, purchases_to_frame
from dietapp.database import session_scope
from dietapp.domain import get_food_emoji
from dietapp.repositories import RepositoryError, get_user_purchases
from dietapp.ui import render_sidebar, require_authentication


LOGGER = logging.getLogger(__name__)


def main() -> None:
    st.set_page_config(
        page_title="Analisi acquisti · DietApp", page_icon="📊", layout="wide"
    )
    if not require_authentication():
        st.stop()
    render_sidebar("Analisi acquisti")

    header, back = st.columns([8, 1])
    with header:
        st.title("📊 Analisi degli acquisti")
    with back:
        if st.button("← Dashboard"):
            st.switch_page("pages/1_home.py")

    try:
        with session_scope() as db:
            records = get_user_purchases(db, st.session_state["username"])
    except RepositoryError:
        LOGGER.exception("Purchase history loading failed")
        st.error("Non è stato possibile caricare lo storico.")
        return

    frame = purchases_to_frame(records)
    if frame.empty:
        st.info("Non ci sono ancora dati validi da analizzare.")
        return

    metric_1, metric_2 = st.columns(2)
    metric_1.metric("Liste salvate", frame["Acquisto"].nunique())
    metric_2.metric("Alimenti diversi", frame["Alimento"].nunique())

    st.subheader("Andamento mensile")
    options = (
        frame[["Alimento", "Alimento leggibile", "Unità"]]
        .drop_duplicates()
        .sort_values(["Alimento leggibile", "Unità"])
    )
    options["Etichetta"] = (
        options["Alimento leggibile"] + " (" + options["Unità"] + ")"
    )
    selected_label = st.selectbox("Alimento", options["Etichetta"].tolist())
    selected = options.loc[options["Etichetta"] == selected_label].iloc[0]
    trend_source = frame.loc[
        (frame["Alimento"] == selected["Alimento"])
        & (frame["Unità"] == selected["Unità"])
    ].copy()
    trend_source["Mese"] = trend_source["Data"].dt.to_period("M").astype(str)
    trend = trend_source.groupby("Mese", as_index=False)["Quantità"].sum()
    fig_trend = px.line(
        trend,
        x="Mese",
        y="Quantità",
        markers=True,
        text="Quantità",
        title=(
            f"{get_food_emoji(selected['Alimento'])} {selected_label} · "
            "quantità acquistata"
        ),
    )
    fig_trend.update_traces(textposition="top center")
    fig_trend.update_yaxes(title=f"Quantità ({selected['Unità']})")
    st.plotly_chart(fig_trend, width="stretch")

    st.subheader("Alimenti acquistati più spesso")
    period_label = st.selectbox(
        "Periodo", ["Tutto lo storico", "Ultimi 3 mesi", "Ultimo mese"]
    )
    months = {
        "Tutto lo storico": None,
        "Ultimi 3 mesi": 3,
        "Ultimo mese": 1,
    }[period_label]
    filtered = filter_period(frame, months)
    if filtered.empty:
        st.info("Nessun acquisto nel periodo selezionato.")
        return

    ranking = (
        filtered.groupby(["Alimento", "Alimento leggibile"], as_index=False)[
            "Acquisto"
        ]
        .nunique()
        .rename(columns={"Acquisto": "Frequenza"})
        .nlargest(10, "Frequenza")
    )
    ranking["Alimento"] = ranking.apply(
        lambda row: f"{get_food_emoji(row['Alimento'])} {row['Alimento leggibile']}",
        axis=1,
    )
    fig_ranking = px.bar(
        ranking,
        x="Alimento",
        y="Frequenza",
        text="Frequenza",
        title=f"Presenza nelle liste · {period_label.lower()}",
    )
    fig_ranking.update_traces(textposition="outside")
    fig_ranking.update_yaxes(title="Numero di liste")
    st.plotly_chart(fig_ranking, width="stretch")

    with st.expander("Dati recenti"):
        recent = frame.sort_values("Data", ascending=False)[
            ["Data", "Alimento leggibile", "Quantità", "Unità"]
        ].head(100)
        st.dataframe(recent, hide_index=True, width="stretch")


if __name__ == "__main__":
    main()
