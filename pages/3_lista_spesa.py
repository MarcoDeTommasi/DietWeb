import pandas as pd
import streamlit as st
import numpy as np
from datetime import datetime
from utils_dicts import  giorni_map, emoji_map
from utils import get_food_emoji
from utils_db import save_spesa,get_user_spesa
from utils_dicts import list_of_days,list_of_meals
from sidebar import mostra_sidebar

st.set_page_config(layout="wide")
st.session_state['pagina_corrente']="lista_spesa"
mostra_sidebar()

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
        elementi_da_comprare[food] = {}
        if food in food_you_have.keys():
            elementi_da_comprare[food]['Quantità'] = food_required[food]['Quantità'] - food_you_have[food]['Quantità']
        else:
            elementi_da_comprare[food]['Quantità'] = food_required[food]['Quantità']
        elementi_da_comprare[food]['Unità'] =  food_required[food]['Unità']
    return elementi_da_comprare

# Funzione per generare l'output della lista della spesa
def Output_lista_settimana(diet_dict,inventario_dict, list_of_days_selected):

    dict_needed = {}
    for giorni in list_of_days_selected:
        for meal in list_of_meals:
            for alimento in diet_dict[giorni][meal]:
                if alimento in list(dict_needed.keys()):
                    dict_needed[alimento]['Quantità'] += diet_dict[giorni][meal][alimento]['Quantità']
                else:
                    dict_needed[alimento] = {}
                    dict_needed[alimento]['Quantità'] = diet_dict[giorni][meal][alimento]['Quantità']
                dict_needed[alimento]['Unità'] = diet_dict[giorni][meal][alimento]['Unità']

    elementi_da_comprare = cibo_settimana_da_Acquistare(inventario_dict, dict_needed)
    return_dict = elementi_da_comprare.copy()
    for key in elementi_da_comprare.keys():
        if elementi_da_comprare[key]['Quantità'] <= 0:
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
# Funzione principale
def main():
    col1,col2 = st.columns([9,1])
    with col1:  
       st.title("🛒 Lista Della Spesa")
    with col2:
        if st.button("⬅️ Indietro"):
            st.switch_page("pages/1_home.py")
    # Layout a colonne per posizionare il bottone in alto a destra
    
    # Prima espansione: Elaborazione lista della spesa
    st.subheader("Seleziona i giorni per cui vuoi fare spesa!")
    giorni_selezionati = st.multiselect("Scegli i giorni:", ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"])
    
    if len(giorni_selezionati) == 0:
        st.warning("Seleziona almeno un giorno per procedere!")
        return
    
    st.divider()
    st.subheader("Muovi il cursore fino ad indicare quanto cibo ti resta in dispensa per ogni alimento!")
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

        steps = 10 if max_quantita >= 200 else 5 if 100 <= max_quantita <= 200 else 1


        quantita_selezionata = st.slider(
            f"{emoji_name} {alimento.replace('_', ' ')} (max: {max_quantita} {unit})",
            min_value=0,
            max_value=max_quantita,
            value=max_quantita // 2,
            step=steps,
            key=f"slider_{alimento}"
        )
        dict_to_fill[alimento] = {'Quantità': quantita_selezionata, 'Unità': unit}

    if st.button("✔️ Submit List"):
        if "lista_spesa" not in st.session_state:
            st.session_state["lista_spesa"] = {}

        # Filtra solo gli alimenti con quantità maggiore di 0
        inventario = {k: v for k, v in dict_to_fill.items() if v['Quantità'] > 0}
        st.session_state["lista_spesa"] = Output_lista_settimana(st.session_state['dict_lunch'],inventario,giorni_selezionati)

    if "lista_spesa" not in st.session_state:
        st.session_state["lista_spesa"] = {}

    lista_spesa = st.session_state["lista_spesa"]

    if lista_spesa:
        col1, col2, col3 = st.columns([1, 4, 1])
        with col1:
            st.subheader("🛒 Lista della spesa:")
        with col3:
            if st.button("💾 Spesa nello storico"):
                date_now = datetime.now().strftime("%d-%m-%y")
                if save_spesa(st.session_state['username'], date_now, lista_spesa):
                    st.success("🛒 Lista della spesa salvata con successo!")
                else:
                    st.error("Errore nel salvataggio 💾")

        # Creazione del DataFrame
        df_spesa = pd.DataFrame([
            (alimento.replace("_", " "), dati["Quantità"], dati["Unità"])
            for alimento, dati in lista_spesa.items()
        ], columns=["Alimento", "Quantità", "Unità"])

        # Aggiungi la colonna 'Acquistato' come checkbox
        if "Acquistato" not in df_spesa.columns:
            df_spesa["Acquistato"] = False

        # Editor della lista della spesa con checkbox
        selected_rows = st.data_editor(df_spesa[["Acquistato", "Alimento", "Quantità", "Unità"]],
                                    use_container_width=True,
                                    hide_index=True,
                                    column_config={"Acquistato": st.column_config.CheckboxColumn("Acquistato")},
                                    key="df_spesa_editor")

        # Verifica se tutti gli elementi sono stati acquistati
        if selected_rows["Acquistato"].all():
            st.success("🎉 Tutti gli alimenti sono stati acquistati!")
            st.session_state["lista_spesa"] = {}  # Reset della lista nella sessione
            st.rerun()
    else:
        st.warning("🛒 Lista della spesa non ancora generata!")

    st.divider()

if __name__ == "__main__":
    if "authentication_status" in st.session_state.keys() and st.session_state["authentication_status"]:
        if 'dict_lunch' in st.session_state.keys():
            dict_lunch = st.session_state['dict_lunch']
            main()
        else:
            st.error("❌ Errore nel caricamento della dieta, impossibile accede al generatore! ")
    else:
        st.error("❌ Not Authenticated! ")

