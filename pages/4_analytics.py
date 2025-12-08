import pandas as pd
import streamlit as st
import plotly.express as px
from database import get_db
from utils_db import get_user_spesa
from utils import get_food_emoji
from sidebar import mostra_sidebar
from upload_diet import create_conversion_dict

st.set_page_config(layout="wide")
st.session_state['pagina_corrente']="analytics"
mostra_sidebar()
db = next(get_db())


def analitics_eval():
    # Supponiamo che la lista contenga elementi con dict_spesa e data
    lista_spesa = get_user_spesa(db, st.session_state["username"])  # Lista di tuple (dict_spesa, data)

    # Creiamo una lista per costruire il DataFrame
    data_for_df = []
    for dict_spesa, data in lista_spesa:
        # Aggiungi ogni elemento come una riga del DataFrame
        data_for_df.append({"Lista Spesa": dict_spesa, "Data": data})

    # Creiamo il DataFrame
    df_spesa = pd.DataFrame(data_for_df)
    # Convertiamo la colonna 'Data' in formato datetime
    df_spesa['Data'] = pd.to_datetime(df_spesa['Data'], format="%Y-%m-%d", errors='coerce', utc=True)
    # Rimuoviamo le righe con valori NaT nella colonna 'Data'
    df_spesa = df_spesa.dropna(subset=['Data'])
    
    food_list = st.session_state.get('food_list', [])
    converted_dict = create_conversion_dict(food_list)

    flattened_data = []
    # Iteriamo attraverso ogni riga del DataFrame
    for _, row in df_spesa.iterrows():
        data = pd.to_datetime(row['Data'])
        # Normalizziamo le chiavi del dizionario "Lista Spesa"
        lista_spesa = {k: v for k, v in row['Lista Spesa'].items()}
        
        # Iteriamo attraverso ogni alimento nel dizionario "Lista_spesa"
        for alimento, details in lista_spesa.items():
            flattened_data.append({
                "Alimento": alimento,
                "Data": data,
                "Mese": data.strftime('%m-%Y'),  # Usa strftime per formattare il mese
                "Quantità": details["Quantità"],
                "Unità": details["Unità"]
            })

    df_trend = pd.DataFrame(flattened_data)

    df_trend = df_trend.groupby(['Mese', 'Alimento'])['Quantità'].sum().reset_index()

    st.title("📊 Analisi degli Acquisti")
    # 📉 **Andamento Consumo nel Tempo**

    # 📉 Andamento Consumo nel Tempo (Aggregato Mensile con Unità)
    st.subheader("📉 Andamento degli acquisti nel Tempo per Alimento")

    # Creiamo un dizionario per mappare le unità di misura
    unita_dict = {}
    for _, row in df_spesa.iterrows():
        for alimento, info in row['Lista Spesa'].items():
            unita_dict[alimento] = info['Unità']

    # Aggiungiamo la colonna 'Unità' a df_trend
    df_trend['Unità'] = df_trend['Alimento'].map(unita_dict)
    df_trend['Mese'] = df_trend['Mese'].astype(str)
    df_trend['Alimento_Leggibile'] = df_trend['Alimento'].apply(lambda x: converted_dict.get(x, x))

    # Selezione alimento
    alimento_sel_leg = st.selectbox("Seleziona un alimento", df_trend['Alimento_Leggibile'].unique())
    alimento_sel = df_trend[df_trend['Alimento_Leggibile'] == alimento_sel_leg]['Alimento'].iloc[0]

    # Aggiungi emoji al nome dell'alimento selezionato
    alimento_sel_emoji = get_food_emoji(alimento_sel)
    alimento_sel_display = f"{alimento_sel_emoji} {alimento_sel_leg}"

    # Filtriamo i dati per l'alimento selezionato
    df_trend_selected = df_trend[df_trend['Alimento'] == alimento_sel]
    df_trend_selected['Quantità'] = df_trend_selected['Quantità'].astype(float)


    # Creiamo il grafico con un solo punto per mese
    fig_trend = px.line(
        df_trend_selected, 
        x='Mese', 
        y='Quantità', 
        title=f'Acquisto di "{alimento_sel_display}" storico', 
        markers=True,
        text=df_trend_selected['Quantità']
    )

    # Aggiorniamo le etichette dell'asse Y
    fig_trend.update_traces(textposition="top center")

    # Aggiorniamo l'asse X per mostrare solo mese e anno
    fig_trend.update_xaxes(
        type='category',
        title="Mese e Anno"
    )
    fig_trend.update_yaxes(
        type='linear',
        title=f"Quantità ({str( df_trend_selected.iloc[0]['Unità'])})"
    )

    st.plotly_chart(fig_trend, width="stretch")

    # 📊 Classifica Cibi più Consumati
    # Selezione intervallo temporale
    # 🏆 **Classifica Cibi Più Acquistati (per frequenza)**
    st.subheader(f"🏆 Classifica Cibi più Acquistati")

    intervallo_sel = st.selectbox("Seleziona intervallo temporale", ["Overall", "Ultimi 3 Mesi", "Ultimo Mese"])

    # Calcoliamo la data di oggi

    mese_corrente = pd.to_datetime("today").month
    anno_corrente = pd.to_datetime("today").year

    # Filtriamo in base all'intervallo temporale
    if intervallo_sel == "Ultimi 3 Mesi":
        df_filtrato = df_trend[
            df_trend['Mese'].apply(lambda x: int(x.split('-')[0])) >= (mese_corrente - 3)
        ]
    elif intervallo_sel == "Ultimo Mese":
        df_filtrato = df_trend[
            df_trend['Mese'].apply(lambda x: int(x.split('-')[0])) == mese_corrente
        ]
    else:
        df_filtrato = df_trend
    # Controllo se il DataFrame filtrato è vuoto
    if df_filtrato.empty:
        st.warning(f"Nessun dato disponibile per l'intervallo temporale selezionato: {intervallo_sel}")
    else:
        # Conta quante volte ogni alimento appare nel periodo selezionato
        df_classifica_frequenza = df_filtrato.groupby(['Alimento', 'Unità']).size().reset_index(name='Frequenza')

        # Ordina gli alimenti per frequenza (dal più acquistato al meno acquistato)
        df_classifica_frequenza = df_classifica_frequenza.sort_values('Frequenza', ascending=False)

        # Selezioniamo solo i top 5 alimenti
        df_classifica_frequenza = df_classifica_frequenza.head(5)
        df_classifica_frequenza['Alimento_Leggibile'] = df_classifica_frequenza['Alimento'].apply(lambda x: converted_dict.get(x, x))

        # Aggiungiamo l'emoji accanto al nome dell'alimento
        df_classifica_frequenza['Alimento_Emoji'] = df_classifica_frequenza['Alimento'].apply(get_food_emoji)
        df_classifica_frequenza['Alimento_Emoji'] = df_classifica_frequenza['Alimento_Emoji'] + " " + df_classifica_frequenza['Alimento_Leggibile']

        # Creiamo la colonna con quantità etichettata per le unità
        df_classifica_frequenza['Quantità_label'] = df_classifica_frequenza.apply(
            lambda row: f"{row['Frequenza']} volte" if row['Unità'] == 'grammi' else f"{row['Frequenza']} volte",
            axis=1
        )

        # **Grafico Classifica Cibi (per frequenza)**
        fig_classifica_frequenza = px.bar(
            df_classifica_frequenza, 
            x='Alimento_Emoji', 
            y='Frequenza', 
            title=f"Cibi più Acquistati per Frequenza - {intervallo_sel}", 
            text=df_classifica_frequenza['Quantità_label']
        )

        # Aggiorniamo l'asse X per mostrare solo mese e anno
        fig_classifica_frequenza.update_xaxes(
            type='category',
            title="Alimento"
        )

        # Posizioniamo le etichette sopra le barre
        fig_classifica_frequenza.update_traces(textposition="outside")

        st.plotly_chart(fig_classifica_frequenza, width="stretch")

if __name__ == "__main__":
    if "authentication_status" in st.session_state.keys() and st.session_state["authentication_status"]:
        
        if 'username' in st.session_state.keys() and 'dict_lunch' in st.session_state.keys():
            if len(get_user_spesa(db, st.session_state['username']))>0:
                analitics_eval()
            else: 
                st.error("❌ Errore nel caricamento della pagina! Dati Insufficienti!")
                if st.button("⬅️ Indietro"):
                    st.switch_page("pages/1_home.py")
        else:
            st.error("❌ Errore nel caricamento della pagina! Username Invalido!")
            
    else:
            st.error("❌ Not Authenticated! ")
