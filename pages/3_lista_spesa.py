import pandas as pd
import streamlit as st
import numpy as np
from datetime import datetime
from utils_dicts import  giorni_map, emoji_map
from utils import get_food_emoji

st.set_page_config(layout="wide",initial_sidebar_state="collapsed")

# Funzione che converte dict_lunch in dict_giorni
def convert_to_dict_giorni(dict_lunch):
    dict_giorni = {}
    
    for giorno, pasti in dict_lunch.items():
        dict_giorni[giorno] = {}
        
        # Iteriamo sui pasti della giornata
        for pasto, alimenti in pasti.items():
            for alimento, info in alimenti.items():
                quantita = info['Quantità']
                dict_giorni[giorno][alimento] = dict_giorni[giorno].get(alimento, 0) + quantita
                
    return dict_giorni

# Funzione per calcolare quanto cibo è necessario acquistare
def cibo_settimana_da_Acquistare(food_you_have, food_required):
    elementi_da_comprare = {}
    for food in food_required.keys():
        if food in food_you_have.keys():
            elementi_da_comprare[food] = food_required[food] - food_you_have[food]
        else:
            elementi_da_comprare[food] = food_required[food]
    return elementi_da_comprare

# Funzione per generare l'output della lista della spesa
def Output_lista_settimana(dict_elementi, list_of_days):

    dict_giorni= convert_to_dict_giorni(st.session_state['dict_lunch'])

    dict_output = {}
    for giorni in list_of_days:
        for alimento in C[giorni]:
            if alimento in list(dict_output.keys()):
                dict_output[alimento] += dict_giorni[giorni][alimento]
            else:
                dict_output[alimento] = dict_giorni[giorni][alimento]

    elementi_da_comprare = cibo_settimana_da_Acquistare(dict_elementi, dict_output)
    return_dict = elementi_da_comprare.copy()
    for key in elementi_da_comprare.keys():
        if elementi_da_comprare[key] <= 0:
            del return_dict[key]

    return return_dict

# Funzione per selezionare i giorni della settimana
def seleziona_giorni():
    giorni_settimana = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
    
    # Crea una lista per i giorni selezionati
    giorni_selezionati = []

    # Mostra i checkbox in orizzontale
    st.write("Seleziona i giorni della settimana:")
    
    # Usa colonne per allineare i checkbox orizzontalmente
    cols = st.columns(7)  # Crea 7 colonne per i 7 giorni della settimana
    for i, giorno in enumerate(giorni_settimana):
        with cols[i]:
            if st.checkbox(giorno):
                giorni_selezionati.append(giorno)
    
    return giorni_selezionati

# Funzione per ottenere l'unità di misura
def get_food_unit(food_name):
    liquid_foods = {"Latte", "Succo di Frutta"}  # Liquidi in ml
    piece_foods = {"Uova", "Frutta", "Frutta Secca"}  # Pezzi (pz)
    default_unit = "g"  # Tutto il resto in grammi

    readable_name = food_name.replace("_", " ")
    if readable_name in liquid_foods:
        return "ml"
    elif readable_name in piece_foods:
        return "pz"
    else:
        return default_unit

# Funzione per suggerire il prossimo pasto
def suggerisci_pasto():
    ora_corrente = datetime.now().hour
    giorno_corrente = datetime.now().strftime("%A")  # Ottiene il giorno in inglese
    giorno_italiano = giorni_map[giorno_corrente]

    # Determina il tipo di pasto in base all'ora
    if ora_corrente < 10:
        pasto_corrente = "Colazione"
    elif 10 <= ora_corrente < 12:
        pasto_corrente = "SpuntinoMattina"
    elif 12 <= ora_corrente < 15:
        pasto_corrente = "Pranzo"
    elif 15 <= ora_corrente < 18:
        pasto_corrente = "SpuntinoPomeriggio"
    else:
        pasto_corrente = "Cena"

    # Trova i suggerimenti per il giorno corrente e il pasto
    pasti_del_giorno = dict_lunch.get(giorno_italiano, {})
    cibi_suggeriti = pasti_del_giorno.get(pasto_corrente, {})

    # Costruisci il messaggio con emoji
    if cibi_suggeriti:
        messaggio = f"Prossimo pasto {pasto_corrente.replace('_', ' ').capitalize()}:\n"
        for alimento, info in cibi_suggeriti.items():
            emoji = get_food_emoji(alimento)
            quantity = info['Quantità']
            unit = info['Unità']
            messaggio += f"- {emoji} {alimento.replace('_', ' ')} : {quantity} {unit}\n"
    else:
        messaggio = "Non ci sono suggerimenti disponibili per il tuo pasto attuale."

    return messaggio

# Funzione principale
def main():
    st.title("Lista Della Spesa 🛒")
    # Layout a colonne per posizionare il bottone in alto a destra
    # Sezione per suggerimento del prossimo pasto
    st.subheader("🍽️ Suggerimento per il prossimo pasto")
    st.write(suggerisci_pasto())
    
    # Prima espansione: Elaborazione lista della spesa
    with st.expander("1. Elaborazione automatica della lista della spesa in base agli alimenti in dispensa", expanded=False):
        st.subheader("Seleziona i giorni per cui vuoi fare spesa!")
        giorni_selezionati = st.multiselect("Scegli i giorni:", ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"])
        
        if len(giorni_selezionati) == 0:
            st.warning("Seleziona almeno un giorno per procedere!")
            return
        
        st.divider()
        st.subheader("Muovi il cursore fino a quanto cibo ti resta in dispensa per ogni tipo!")
        dict_to_fill = {}
        dict_max_elements = {}
        dict_giorni= convert_to_dict_giorni(st.session_state['dict_lunch'])

        for giorno in giorni_selezionati:
            for alimento, quantita in dict_giorni.get(giorno, {}).items():
                dict_max_elements[alimento] = dict_max_elements.get(alimento, 0) + quantita

        # Crea slider per ogni alimento con emoji e unità di misura
        for alimento, max_quantita in dict_max_elements.items():
            emoji_name = get_food_emoji(alimento)
            unit = get_food_unit(alimento)

            if max_quantita >= 200:
                steps = 10
            elif 100 <= max_quantita <= 200:
                steps = 5
            else: 
                steps = 1

            dict_to_fill[alimento] = st.slider(
                f"{emoji_name} {alimento.replace('_', ' ')} (max: {max_quantita} {unit})",
                min_value=0,
                max_value=max_quantita,
                value=max_quantita // 2,
                step=steps,
                key=f"slider_{alimento}"
            )

    # Bottone per calcolare la lista della spesa
    if st.button("✔️ Submit List"):
        if "lista_spesa" not in st.session_state:
            st.session_state["lista_spesa"] = {}
        # Aggiorna la lista della spesa nello stato della sessione
        st.session_state["lista_spesa"] = {k: v for k, v in dict_to_fill.items() if v > 0}

    # Recupera la lista della spesa dallo stato della sessione
    if "lista_spesa" not in st.session_state:
        st.session_state["lista_spesa"] = {}

    lista_spesa = st.session_state["lista_spesa"]

    if len(lista_spesa) > 0:
        st.subheader("🛒 Lista della spesa:")
        # Creazione del DataFrame
        df_spesa = pd.DataFrame(
            [(get_food_emoji(alimento) + alimento.replace("_", " "), quantita, get_food_unit(alimento)) 
            for alimento, quantita in lista_spesa.items()],
            columns=["Alimento", "Quantità", "Unità"]
        )
        
        # Aggiungi la colonna 'Acquistato' come checkbox
        if "Acquistato" not in df_spesa.columns:
            df_spesa["Acquistato"] = False
        
        # Se la checkbox viene selezionata, aggiorna lo stato
        selected_rows = st.data_editor(df_spesa[["Acquistato","Alimento", "Quantità", "Unità"]],
                                    use_container_width=True,
                                    hide_index=True,
                                    column_config={"Acquistato": st.column_config.CheckboxColumn("Acquistato")},
                                    key="df_spesa_editor")
        
        # Verifica se tutte le righe sono state selezionate come acquistate
        if selected_rows["Acquistato"].all():
            st.success("🎉 Tutti gli alimenti sono stati acquistati!")
            
            # Nascondi la lista
            st.session_state["lista_spesa"] = []  # Reset della lista nella sessione
            st.rerun()
    else:
        st.warning("🛒 Lista della spesa non ancora generata!")
    st.divider()

if __name__ == "__main__":
    if 'dict_lunch' in st.session_state.keys():
        dict_lunch = st.session_state['dict_lunch']
        main()
    else:
        st.error("Errore nel caricamento della dieta, impossibile accede al generatore! ")

