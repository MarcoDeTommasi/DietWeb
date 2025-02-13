from huggingface_hub import InferenceClient
import streamlit as st
import fitz
import os

# Configurazione del client Hugging Face
client = InferenceClient(
    model="mistralai/Mistral-7B-Instruct-v0.3",  # Modello specificato
    token="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",  # Sostituisci con il tuo token
    timeout=120  # Timeout per richieste lunghe
)

# Template del prompt
template = """Ti darò un piano alimentare personalizzato per un utente. In questo piano sono presenti le linee guida alimentari per ogni giorno della settimana e per ogni pasto.
Ti chiederò cosa è consigliato mangiare per un dato pasto in un dato giorno e tu devi rispondere elencando i cibi e le quantità riportate.

Ogni giorno ha questi possibili pasti:

['Colazione','Spuntino','Pranzo','Cena']

NOTA: riportami 2 spuntini, uno mattutino e uno pomeridiano,
se ti chiedo di parlare di uno spuntino e aggiungo mattutino o pomeridiano riportami rispettivamente quello fra la colazione e il pranzo e quello fra il pranzo e la cena

NOTA: riportami la risposta come una lista Python.

DEVI Rispettare questo formato, la quantità e sempre riportata:
[ 'alimento1 quantita', 'alimento2 quantita', 'alimento3 quantita']

Riporta solo il tipo di alimenti e la quantità, evita aggettivi:

Es. Latte parzialmente scremato 200ml -> Latte 200ml
Es. Yogurt Greco 150g-> Yogurt 150g

Tralascia tutti gli aggettivi

se come unità di misura compaiono "g" "ml" riportale, in caso di assenza utilizza "pz"
Le unità di misura non devono comparire fra parentesi

riportami solo i cibi relativi al pasto indicato.

IMPORTANTE: EVITA LE ALTERNATIVE

NOTA: NON FORNIRE ALTRO TESTO OLTRE ALLA LISTA

{context}

Question: {question}
"""

# Lista dei giorni della settimana
list_of_days = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica']

def process_diet_pdf(context, question):
    """
    Processa la richiesta dietetica utilizzando Hugging Face API.
    """
    # Prepara il prompt personalizzato
    custom_prompt = template.format(context=context, question=question)

    # Struttura del messaggio
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Use the given context to answer questions accurately."},
        {"role": "user", "content": custom_prompt}
    ]
    
    try:
        # Eseguire la richiesta al modello
        completion = client.chat_completion(
            messages=messages,
            max_tokens=500,
            temperature=0.01
        )
        
        # Estrarre e restituire la risposta
        answer = completion["choices"][0]["message"]["content"].strip()
        return answer
    except Exception as e:
        raise ValueError(f"Errore durante l'elaborazione della domanda: {e}")



def parse_meals_with_llm(lines,list_days,n_value = 5):

    # Esegui il task di question answering per estrarre i pasti
    answers = {}
    
    max_length = 500  # Imposta il numero di caratteri che desideri
    n_value = 5       # Numero di righe da cui partire

    for day in list_days:
      answers[day] = {}
      for ind, el in enumerate(lines):
          if day.lower() in el.lower():
              relevant_ind = ind

      # Trova l'inizio del "chunk" a partire da n_value righe prima dell'indice trovato
      lower_index = relevant_ind - n_value if relevant_ind - n_value >= 0 else 0

      # Iniziamo a prendere il testo dal lower_index e espandiamo solo verso il basso
      context = ""
      while len(context) < max_length and lower_index < len(lines):
          context += lines[lower_index] + "\n"
          lower_index += 1

      # Se il "chunk" è più lungo di max_length, lo troncano
      context = context[:max_length] if len(context) > max_length else context

      print(context)

      for meal in ["Colazione", "Pranzo", "Cena", "SpuntinoMattina","SpuntinoPomeriggio"]:
          question = f"Cosa devo mangiare di {day} per {meal}?"
          answer = process_diet_pdf(context,question)
          answers[day][meal]=answer
          print(f"{day}-{meal}: {answer}")
      

    # Restituisci il dizionario con le risposte per il giorno specificato
    return answers

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

def upload_diet_page():
    st.title("📤 Carica la tua Dieta")
    st.write("Trascina qui il file .pdf della tua dieta.")

    # Drag-and-drop per il caricamento del file
    uploaded_file = st.file_uploader("Carica un file .pdf:", type=["pdf"], accept_multiple_files=False)

    if uploaded_file:
        st.success(f"✅ File '{uploaded_file.name}' caricato con successo!")

        # Estrazione del contenuto e parsing
        lines = parse_pdf_to_dict(uploaded_file)
        dict_lunch = parse_meals_with_llm(lines,list_of_days)

        st.subheader("📋 Piano nutrizionale estratto:")
        st.write(dict_lunch)

        # Salva il dizionario nello stato della sessione
        st.session_state["dict_lunch"] = dict_lunch

if __name__ == "__main__":
    upload_diet_page()