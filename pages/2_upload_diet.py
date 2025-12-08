import streamlit as st
import fitz
import pandas as pd
import json
from utils_db import  save_diet,save_food_list
from sidebar import mostra_sidebar
from upload_diet import extract_food_list, split_text_with_overlap, get_food_list_from_pdf,create_conversion_dict, convert_quantities_to_int
from utils_dicts import list_of_days, list_of_meals, unit_options

st.set_page_config(layout="wide")
st.session_state['pagina_corrente'] = "upload_diet"
mostra_sidebar()

def edit_meal_data():
    """Permette all'utente di modificare la dieta passo dopo passo."""
    
    dict_lunch = st.session_state["dict_lunch"]
    days = list(dict_lunch.keys())
    reversed_converted_dict = {v: k for k, v in st.session_state['converted_food_dict'].items()}
    current_day = days[st.session_state["current_day"]]
    st.subheader(f"📅 Giorno: {current_day}")
    
    meal_data = dict_lunch[current_day]
    
    # Creiamo una disposizione delle tabelle in più colonne
    cols = st.columns(3)  # 3 colonne per ogni riga
    edited_data = {}  # Dizionario temporaneo per memorizzare i dati modificati
    for idx, meal in enumerate(list_of_meals):
        with cols[idx % 3]:  # Disposizione ciclica delle tabelle
            st.write(f"### 🍽 {meal}")
            data = []
            for alimento, details in meal_data[meal].items():
                alimento = st.session_state['converted_food_dict'].get(alimento, alimento)
                quantity = details["Quantità"]
                unit = details["Unità"]
                data.append([alimento, quantity, unit])

            # Creazione del DataFrame per il pasto
            df = pd.DataFrame(data, columns=["Alimento", "Quantità", "Unità"])
            # Mostriamo la tabella modificata 
            edited_df = st.data_editor(df,
                                       key=f"Data_editor_{current_day}_{meal}",
                                       width="content",
                                       column_config={
                                            "Alimento": st.column_config.SelectboxColumn("Alimento", options=list(st.session_state['converted_food_dict'].values())),
                                            "Quantità": st.column_config.NumberColumn("Quantità", format="%d", step=1,default=0),
                                           "Unità": st.column_config.SelectboxColumn("Unità", options=['g', 'ml', 'pz']),
                                       },
                                       num_rows="dynamic")

            meal_new_data = {}
            for index, row in edited_df.iterrows():
                alimento = row["Alimento"]
                quantita = row["Quantità"]
                unita = row["Unità"]

                # Se `alimento` è una lista, prendi il primo elemento, altrimenti usa il valore direttamente
                if isinstance(alimento, list):
                    alimento = alimento[0] if alimento else ""  # Usa "" se la lista è vuota

                # Se `quantita` è una lista, prendi il primo elemento, altrimenti usa il valore direttamente
                if isinstance(quantita, list):
                    quantita = quantita[0] if quantita else 0  # Usa 0 se la lista è vuota

                # Se `unita` è una lista, prendi il primo elemento, altrimenti usa il valore direttamente
                if isinstance(unita, list):
                    unita = unita[0] if unita else "g"  # Usa "g" come valore predefinito

                if pd.notna(alimento) and alimento.strip():  # Controlla che il nome dell'alimento non sia vuoto
                    alimento = reversed_converted_dict.get(alimento, alimento)
                    meal_new_data[alimento] = {
                        "Quantità": 0 if pd.isna(quantita) else quantita,  # Se è NaN, metti 0
                        "Unità": "g" if pd.isna(unita) or not unita else unita,  # Se è NaN o vuoto, metti "g"
                    }

                
            # Salva meal_new_data in edited_data
            edited_data[meal] = meal_new_data
    col1, col2, col3 = st.columns([1, 4, 1])
    
    # Salvataggio delle modifiche nel dizionario solo quando l'utente preme uno dei bottoni
    with col1:
        if st.button("⬅️ Giorno Precedente", disabled=st.session_state['current_day'] == 0):
            # Non aggiornare il dizionario, solo cambiamo il giorno
            dict_lunch[current_day] = edited_data  # Salviamo i dati modificati nel dizionario
            st.session_state["dict_lunch"] = dict_lunch  # Aggiorniamo il dizionario globale
            st.session_state["current_day"] -= 1
            st.rerun()
    
    with col3:
        if st.button("✅ Conferma e Avanti"):
            # Aggiorniamo il dizionario con i dati modificati solo quando l'utente conferma
            dict_lunch[current_day] = edited_data  # Salviamo i dati modificati nel dizionario
            st.session_state["dict_lunch"] = dict_lunch  # Aggiorniamo il dizionario globale
            if st.session_state["current_day"] < len(days) - 1:
                st.session_state["current_day"] += 1
            else:
                st.session_state["review_complete"] = True
            st.rerun()

def check_invalid_quantities(d,error_container):
    """
    Controlla se ci sono valori None nelle chiavi o quantità pari a 0/None.
    Se trova errori, mostra un messaggio di errore e un DataFrame con i problemi.
    """
    invalid_entries = []

    for day, meals in d.items():
        for meal, foods in meals.items():
            for alimento, details in foods.items():
                if alimento is None or details["Quantità"] in [None, 0]:  
                    invalid_entries.append([day, meal, alimento, details["Quantità"], details["Unità"]])

    with error_container:  # Scrive nel container per restare visibile
        st.empty()  # Reset dello spazio
        if invalid_entries:
            st.error("❌ Errore! Alcuni alimenti hanno quantità non valide (0 o None). Correggi prima di procedere.")
            
            # Creazione della tabella solo con le righe problematiche
            df = pd.DataFrame(invalid_entries, columns=["📅 Giorno", "🍽 Pasto", "🥗 Alimento", "⚖️ Quantità", "📏 Unità"])
            st.data_editor(df, key="invalid_entries")
            
            return False  # Indica che ci sono errori
        
    return True  # Indica che è tutto ok

def upload_diet_page():
 
    col1, col2 = st.columns([9, 1])
    with col1:
        st.title("📤 Carica la tua Dieta")
    with col2:
        if st.button("⬅️ Indietro"):
            st.switch_page("pages/1_home.py")

    if "current_day" not in st.session_state:
        st.session_state["current_day"] = 0

    # Placeholder per visualizzare errori in alto
    if "error_messages" not in st.session_state:
        st.session_state["error_messages"] = None
    
    if "dict_lunch" not in st.session_state.keys():
        st.session_state["dict_lunch"] = {}
        for day in list_of_days:
            st.session_state["dict_lunch"][day] = {}
            for meal in list_of_meals:
                st.session_state["dict_lunch"][day][meal] = {}
        st.rerun()

    if 'food_list' not in st.session_state:
        st.session_state['food_list'] = []
    
    error_container = st.container()  

    if  len(st.session_state['food_list']) == 0 :
        st.write("Trascina qui il file .pdf della tua dieta per acquisire in automatico la lista degli alimenti")
        uploaded_file = st.file_uploader("Carica un file .pdf:", type=["pdf"], accept_multiple_files=False)

        if uploaded_file is not None:
            st.warning(f"🔄 Attendere l'elaborazione del documento '{uploaded_file.name}'..")
            food_list = get_food_list_from_pdf(uploaded_file)
            converted_food_dict = create_conversion_dict(food_list)
            st.session_state['converted_food_dict'] = converted_food_dict
            st.session_state['food_list'] = food_list
            st.rerun()
    else:
        st.success("✅ Lista degli alimenti gia caricata con successo!")
        st.session_state['converted_food_dict'] = create_conversion_dict(st.session_state['food_list'])

    # Mostra la lista degli alimenti in un editor interattivo
    st.subheader("Modifica la lista degli alimenti")

    st.session_state['converted_food_dict'] = create_conversion_dict(st.session_state['food_list'])

    converted_food_dict = st.session_state['converted_food_dict']
    food_list = st.session_state['food_list']

    # Creazione di un DataFrame per mostrare la converted_food_dict
    if len(converted_food_dict) > 0:
        food_df = pd.DataFrame({"Alimenti": list(converted_food_dict.values())})
    else:
        # Inizializza un DataFrame vuoto con la colonna "Alimenti"
        food_df = pd.DataFrame({"Alimenti": [""]})

    # Editor per modificare la lista
    edited_food_df = st.data_editor(
        food_df,
        num_rows="dynamic",  # Permette di aggiungere o rimuovere righe
        width="content",
        key="food_list_editor",
        column_config={
        "Alimenti": st.column_config.TextColumn("Alimenti")  # Configura la colonna come testo
    }
    )

    # Salva le modifiche alla lista
    if st.button("💾 Salva modifiche alla lista"):
        # Aggiorna food_list e converted_food_dict
        new_converted_food_dict = edited_food_df["Alimenti"].dropna().tolist()
        new_food_list = []

        # Controlla duplicati e aggiorna food_list e converted_food_dict
        for item in new_converted_food_dict:
            item_coded = item.lower().replace(" ", "_")
            if item_coded not in new_food_list:  # Evita duplicati
                new_food_list.append(item_coded)

        # Verifica se ci sono duplicati nella lista leggibile
        if len(new_converted_food_dict) != len(set(new_converted_food_dict)):
            st.error("❌ La lista contiene duplicati! Rimuovili prima di salvare.")
        else:
            # Salva le liste aggiornate nello stato della sessione
            st.session_state['food_list'] = new_food_list
            st.session_state['converted_food_dict'] = create_conversion_dict(new_food_list)
            st.success("✅ Lista degli alimenti aggiornata con successo!")
            st.rerun()
    
    st.subheader("📋 Inserisci o Modifica il piano Nutrizionale")

    if "dict_lunch" in st.session_state.keys():
        if "food_list" in st.session_state.keys() and len(st.session_state['food_list']) >0:
            edit_meal_data()

            if st.button("💾 Salva e Invia"):
                is_valid = check_invalid_quantities(st.session_state['dict_lunch'],error_container)
                if is_valid:  # Se tutto è OK, procede con il salvataggio
                    if save_diet(st.session_state['username'], st.session_state['dict_lunch']) and save_food_list(st.session_state['username'], st.session_state['food_list']):
                        st.success("✅ Dati salvati con successo!")
                        st.switch_page("pages/1_home.py")
                else:
                    st.error("❌ Correggi gli errori prima di salvare i dati.")

        else:
            st.error("❌ La lista degli alimenti è vuota. Carica un file PDF o inserisci manualmente gli alimenti.")


if __name__ == "__main__":
    if "authentication_status" in st.session_state.keys() and st.session_state["authentication_status"]:
        if 'username' not in st.session_state.keys() or st.session_state['username'] is None:
            st.error("❌ Errore nel caricamento della pagina, Username assente! ")
        else:
            upload_diet_page()
    else:
        st.error("❌ Not Authenticated! ")