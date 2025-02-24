from huggingface_hub import InferenceClient
import streamlit as st
import fitz
import os
import pandas as pd
import ast
from utils import template
import json
import re
from utils_dicts import list_of_days,list_of_meals
from utils_db import save_diet
from sidebar import mostra_sidebar

# Configurazione del client Hugging Face
client = InferenceClient(
    model="mistralai/Mistral-7B-Instruct-v0.3",  # Modello specificato
    #model="Groq/Llama-3-Groq-8B-Tool-Use",
    token = os.getenv("HUGGINGFACE_API_TOKEN"),  # Sostituisci con il tuo token
    timeout=120  # Timeout per richieste lunghe
)
st.set_page_config(layout="wide")
st.session_state['pagina_corrente']="upload_diet"
mostra_sidebar()

def process_llm_answer(context, max_retries=3):
    """
    Processa la richiesta dietetica utilizzando Hugging Face API.
    """

    messages = [
        {"role": "system", "content": "You are a helpful assistant. Use the given context to answer questions accurately."},
        {"role": "user", "content": context}
    ]
    
    for attempt in range(max_retries):
        try:
            completion = client.chat_completion(
                messages=messages,
                max_tokens=500,
                temperature=0.01
            )
            
            answer = completion["choices"][0]["message"]["content"].strip()
            # Prova a convertire la risposta in lista
             # Prova prima a decodificare come JSON (più sicuro)
            
            answer = '{'+ answer.split('{')[-1].split('}')[0]+'}'
            
            try:
                answer_dict = json.loads(answer)  # Usa json.loads() per gestire stringhe con doppi apici
                if isinstance(answer_dict, dict):
                    return answer_dict
                
            except json.JSONDecodeError:
                pass

            # Se fallisce JSON, prova con ast.literal_eval()
            try:
                answer_dict = ast.literal_eval(answer)
                if isinstance(answer_dict, dict):
                    return answer_dict
            except (ValueError, SyntaxError):
                pass  # Se la conversione fallisce, ritenta la richiesta

        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Errore durante l'elaborazione della domanda dopo {max_retries} tentativi: {e}")
                return {}
    
    return {}
    

def convert_quantities_to_int(d):
    for key, value in d.items():
        if isinstance(value, dict):
            convert_quantities_to_int(value)  # Ricorsione per scendere nei sotto-dizionari
        elif key == "Quantità" and isinstance(value, float) and value.is_integer():
            d[key] = int(value)  # Conversione a intero solo se non ci sono decimali
    return d

def chunk_text_by_day(lines):
    """
    Segmenta il testo in base ai giorni della settimana.
    """
    chunks = {}
    current_day = None
    current_chunk = []

    for line in lines:
        # Cerca i giorni della settimana nel testo
        for day in list_of_days:
            if day.lower()[:-1] in line.lower():
                # Se c'era un giorno precedente, aggiungi il chunk
                if current_day:
                    if current_day in chunks:
                        chunks[current_day].append("\n".join(current_chunk))
                    else:
                        chunks[current_day] = ["\n".join(current_chunk)]  # Aggiungi un nuovo chunk se non esiste
                # Imposta il nuovo giorno e inizia un nuovo chunk
                current_day = day
                current_chunk = [line]
                break  # Esci dal ciclo dei giorni, in modo da non aggiungere la riga al chunk
        else:  # Se nessun giorno è stato trovato nella riga
            if current_day:
                current_chunk.append(line)

    # Aggiungi l'ultimo giorno
    if current_day:
        if current_day in chunks:
            chunks[current_day].append("\n".join(current_chunk))
        else:
            chunks[current_day] = ["\n".join(current_chunk)]

    return chunks
   
def clean_meal_data(dict_lunch):
    """Pulisce i dati nel dizionario dict_lunch, separando quantità e unità, e normalizzando la quantità."""
    
    # Regex per trovare quantità seguita da g/ml/pz, con possibile spazio
    unit_pattern = r"(\d+(?:[-/]\d+)?)(\s?)(g|ml|pz)"
    
    # Itera su tutti i giorni e pasti
    for day in dict_lunch:
        for meal in dict_lunch[day]:
            meal_data = dict_lunch[day][meal]
            cleaned_meal_data = {}

            for alimento, quantita_unita in meal_data.items():
                # Trova la quantità e l'unità nel testo
                match = re.search(unit_pattern, quantita_unita)
                
                if match:
                    # Estrae la quantità e l'unità
                    quantity_str, _, unit = match.groups()
                    # Pulisce la quantità, trattando casi come "4-5" o "5/6"
                    if '-' in quantity_str:
                        # Se la quantità è nel formato "4-5", prendi solo l'ultimo numero
                        quantity = int(quantity_str.split('-')[-1])
                    elif '/' in quantity_str:
                        # Se la quantità è nel formato "5/6", prendi solo l'ultimo numero
                        quantity = int(quantity_str.split('/')[-1])
                    else:
                        # Se è solo un numero, convertilo
                        quantity = int(quantity_str)
                    
                    # Salva il risultato nel nuovo dizionario
                    cleaned_meal_data[alimento] = {"Quantità": quantity, "Unità": unit}
                else:
                    # Se non è possibile trovare una corrispondenza, mantieni il dato originale
                    if '-' in quantita_unita:
                        # Se la quantità è nel formato "4-5", prendi solo l'ultimo numero
                        quantity = int(quantita_unita.split('-')[-1])
                    elif '/' in quantita_unita:
                        # Se la quantità è nel formato "5/6", prendi solo l'ultimo numero
                        quantity = int(quantita_unita.split('/')[-1])
                    else:
                        # Se è solo un numero, convertilo
                        try:
                            quantity = int(quantita_unita)
                        except:
                            quantity = None
                
                    cleaned_meal_data[alimento] = {"Quantità": quantity, "Unità": "pz"}
            
            # Sostituisce il vecchio dizionario con quello pulito
            dict_lunch[day][meal] = cleaned_meal_data
    
    return dict_lunch

def parse_meals_with_llm(lines,list_days):

    # Esegui il task di question answering per estrarre i pasti
    answers = {}
    chunks = chunk_text_by_day(lines)
    for day in list_days:
        answers[day]={}
        for meal in list_of_meals:
            question = f"Cosa devo mangiare di {day} per {meal}?"
            custom_prompt = template.format(context=chunks[day], question=question)
            answer = process_llm_answer(custom_prompt)
            answers[day][meal]=answer
            print(f"{day}-{meal}: {answer}")
      

    # Restituisci il dizionario con le risposte per il giorno specificato
    return answers

def clean_dict_values(d):
    for day, meals in d.items():
        for meal, foods in meals.items():
            for alimento, details in foods.items():
                if details["Quantità"] is None or pd.isna(details["Quantità"]):
                    details["Quantità"] = 0
                if details["Unità"] is None or pd.isna(details["Unità"]):
                    details["Unità"] = "g"
    return d

def parse_pdf_to_dict(pdf_file):
    """
    Estrai il contenuto di un file PDF e crealo in un dizionario strutturato per il piano alimentare.
    """
    # Leggi il PDF
    pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    raw_text = ""

    # Estrai il testo da tutte le pagine
    for page in pdf_document:
        raw_text += page.get_text()

    pdf_document.close()

    lines = raw_text.split("\n")
    lines = [line.strip() for line in lines if line.strip()]  # Rimuove spazi vuoti
    
    return lines

def edit_meal_data():
    """Permette all'utente di modificare la dieta passo dopo passo."""
    
    dict_lunch = st.session_state["dict_lunch"]
    days = list(dict_lunch.keys())
    meals = ["Colazione", "Pranzo", "Cena", "SpuntinoMattina", "SpuntinoPomeriggio"]
    meals_emoji = ["Colazione 🥐", "Pranzo 🍝", "Cena 🥩", "Spuntino Mattutino 🍎", "Merenda Pomeridiana 🍪"]
    
    current_day = days[st.session_state["current_day"]]
    st.subheader(f"📅 Giorno: {current_day}")
    
    meal_data = dict_lunch[current_day]
    
    # Creiamo una disposizione delle tabelle in più colonne
    cols = st.columns(3)  # 3 colonne per ogni riga
    edited_data = {}  # Dizionario temporaneo per memorizzare i dati modificati
    for idx, meal in enumerate(meals):
        with cols[idx % 3]:  # Disposizione ciclica delle tabelle
            st.write(f"### 🍽 {meals_emoji[idx]}")
            data = []
            for alimento, details in meal_data[meal].items():
                quantity = details["Quantità"]
                unit = details["Unità"]
                data.append([alimento, quantity, unit])

            # Creazione del DataFrame per il pasto
            df = pd.DataFrame(data, columns=["Alimento", "Quantità", "Unità"])
            
            # Mostriamo la tabella modificata
            edited_df = st.data_editor(df,
                                       key=f"Data_editor_{current_day}_{meal}",
                                       use_container_width=True,
                                       column_config={
                                           "Unità": st.column_config.SelectboxColumn("Unità", options=['g', 'ml', 'pz'])
                                       },
                                       num_rows="dynamic")

            meal_new_data = {}
            for index, row in edited_df.iterrows():
                alimento = row["Alimento"]
                quantita = row["Quantità"]
                unita = row["Unità"]

                if pd.notna(alimento) and alimento.strip():  # Controlla che il nome dell'alimento non sia vuoto
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
            st.session_state["dict_lunch"] = clean_dict_values(dict_lunch)  # Aggiorniamo il dizionario globale
            st.session_state["current_day"] -= 1
            st.rerun()
    
    with col3:
        if st.button("✅ Conferma e Avanti"):
            # Aggiorniamo il dizionario con i dati modificati solo quando l'utente conferma
            dict_lunch[current_day] = edited_data  # Salviamo i dati modificati nel dizionario
            st.session_state["dict_lunch"] = clean_dict_values(dict_lunch)  # Aggiorniamo il dizionario globale
            if st.session_state["current_day"] < len(days) - 1:
                st.session_state["current_day"] += 1
            else:
                st.session_state["review_complete"] = True
            st.rerun()


def upload_diet_page():
    col1,col2 = st.columns([9,1])
    with col1:  
        st.title("📤 Carica la tua Dieta")
    with col2:
        if st.button("⬅️ Indietro"):
            st.switch_page("pages/1_home.py")

    if 'dict_lunch' not in st.session_state.keys():
        st.write("Trascina qui il file .pdf della tua dieta.")
        uploaded_file = st.file_uploader("Carica un file .pdf:", type=["pdf"], accept_multiple_files=False)
    
        if uploaded_file and 'review_complete' not in st.session_state:
        #st.success(f"✅ File '{uploaded_file.name}' caricato con successo!")
            st.warning(f"🔄 Attendere l'elaborazione del documento '{uploaded_file.name}'..")
            lines = parse_pdf_to_dict(uploaded_file)
            dict_raw = parse_meals_with_llm(lines, list_of_days)
            dict_lunch = clean_meal_data(dict_raw)
            ## Salviamo il dizionario solo se non è già stato elaborato
            st.session_state["dict_lunch"] = dict_lunch
            st.session_state["review_complete"] = False
            st.session_state["current_day"] = 0
            st.rerun()
    
    if "review_complete" in st.session_state and st.session_state["review_complete"]:
        st.subheader("📋 Piano nutrizionale confermato")

        # Mappatura delle emoji per ogni pasto
        base_meal_emojis = {
            "Colazione": "🥐",
            "Pranzo": "🍝",
            "Cena": "🥩",
            "SpuntinoMattina": "🍎",
            "SpuntinoPomeriggio": "🍪"
        }
        meal_emojis={}

        for day in list_of_days:
            for meal in base_meal_emojis:
                if meal in st.session_state['dict_lunch'][day]:
                    meal_emojis[meal] = base_meal_emojis[meal]
                else:
                    meal_emojis[meal] = ""
        # Creazione della lista strutturata per il DataFrame
        data = []
        for day, meals in st.session_state["dict_lunch"].items():
            for meal, foods in meals.items():
                meal_with_emoji = f"{meal_emojis.get(meal, '')} {meal}"  # Aggiunta emoji
                for food, details in foods.items():
                    data.append([day, meal_with_emoji, food, details["Quantità"], details["Unità"]])

        # Creazione del DataFrame con intestazioni chiare
        df = pd.DataFrame(data, columns=["📅 Giorno", "🍽 Pasto", "🥗 Alimento", "⚖️ Quantità", "📏 Unità"])

        # Visualizzazione della tabella interattiva con Streamlit
        st.data_editor(df, use_container_width=True, hide_index=True)
        
        col1, col2, col3 = st.columns([1, 4, 1])  # La colonna centrale è più grande per la spaziatura

        with col1:
            if st.button("⬅️ Giorno Precedente", disabled=st.session_state['current_day'] == 0):
                st.session_state["review_complete"] = False
                st.rerun()

        with col3:  # Sposta "Salva e Invia" tutto a destra
            if st.button("💾 Salva e Invia"):
                
                dict_lunch = convert_quantities_to_int(st.session_state['dict_lunch'])

                if save_diet(st.session_state['username'],dict_lunch):
                    st.success("✅ Dati salvati con successo!")
                    st.switch_page("pages/1_home.py")

    elif "review_complete" in st.session_state and st.session_state['review_complete'] == False:
        st.success(f"✅ AI Review terminata per il documento, Proseguire con la verifica.")
        edit_meal_data()
    
if __name__ == "__main__":
    if "authentication_status" in st.session_state.keys() and st.session_state["authentication_status"]:
        if 'username' not in st.session_state.keys() or st.session_state['username']==None:
            st.error("❌ Errore nel caricamento della pagina, Username assente! ")
        else:
            upload_diet_page()
    else:
        st.error("❌ Not Authenticated! ")


