from utils_dicts import emoji_map
import sqlite3
import streamlit as st
import json
import unicodedata
import spacy
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url=os.getenv("OPENROUTER_API_URL"),
    api_key=os.getenv("OPENROUTER_API_KEY"),  # Assicurati che OPENROUTER_API_KEY sia definito
)
# Inizializza il convertitore per singolari/plurali
nlp = spacy.load("it_core_news_sm")

def to_singular(word):
    """Converte una parola al singolare usando la lemmatizzazione."""
    doc = nlp(word)
    for token in doc:
        return token.lemma_

def normalize_key(key):
    """Normalizza una chiave del dizionario."""
    # Rimuove accenti
    key = ''.join(
        c for c in unicodedata.normalize('NFD', key)
        if unicodedata.category(c) != 'Mn'
    )
    # Converte in minuscolo e sostituisce spazi con _
    key = key.lower().replace(' ', '_')
    # Converte al singolare
    key = to_singular(key)
    return key

def normalize_dict(input_dict):
    """Normalizza tutte le chiavi di un dizionario."""
    return {normalize_key(k): v for k, v in input_dict.items()}


def query_llm(prompt):
    """Invia una query ad un llm tramite OpenRouter."""
    try:
        completion = client.chat.completions.create(
            extra_headers={
                "X-Title": "DietWebApp",  # Sostituisci con il nome del tuo sito/app
            },
            model="openai/gpt-4o",  # Specifica il modello Gemma 3
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=200,
            temperature=0
        )
        # Restituisce il contenuto della risposta
        if hasattr(completion, "choices"):
            return completion.choices[0].message.content
        elif isinstance(completion, dict):
            return completion["choices"][0]["message"]["content"]
    except Exception as e:
        raise Exception(f"Errore durante la query all llm: {str(e)}")

def get_food_emoji(food_name):
    """
    Cerca se una delle parole nella lista si trova nella stringa fornita e restituisce l'emoji corrispondente.
    """
    # Cerca una corrispondenza parziale nel dizionario delle emoji
    for key, emoji in emoji_map.items():
        if key in food_name:  # Confronto case-insensitive
            return f"{emoji}"

    # Emoji predefinita se non ci sono corrispondenze
    return "🥗"

# Template del prompt
template = """Ti darò un piano alimentare personalizzato per un utente. In questo piano sono presenti le linee guida alimentari per ogni giorno della settimana e per ogni pasto.
Ti chiederò cosa è consigliato mangiare per un dato pasto in un dato giorno e tu devi rispondere elencando i cibi e le quantità riportate.

Ogni giorno ha questi possibili pasti:

['Colazione','Spuntino','Pranzo','Cena']

NOTA: riportami 2 spuntini, uno mattutino e uno pomeridiano,
se ti chiedo di parlare di uno spuntino e aggiungo mattutino o pomeridiano riportami rispettivamente quello fra la colazione e il pranzo e quello fra il pranzo e la cena

NOTA: riportami la risposta come un dizionario Python.

DEVI Rispettare questo formato, la quantità e sempre riportata:
{{ 'alimento1 ': 'quantita unit', 'alimento2' : 'quantita unit', 'alimento3' : 'quantita unit'}}

NOTA: se non trovi la quantita e la unit , non riportarmi l'alimento nel dizionario.
NOTA: Utilizza il minor numero di chiavi possibile (alimenti) per creare il dizionario, se ci sono piu verdure ad esempio, riporta solo una chiave
NOTA: LE CHIAVI DEL DIZIONARIO POSSONO ESSERE SOLO CIBI NON PAROLE COME "Alternative" 
NOTA: quantita PUO ESSERE SOLO UN NUMERO INTERO
NOTA: unit PUO' ESSERE solo uno a scelta fra ["g","ml","pz"] E NON DEVE MAI ESSERE VUOTO

Riporta solo il tipo di alimenti e la quantità, evita aggettivi:

Es. Latte parzialmente scremato 200ml -> Latte 200ml
Es. Yogurt Greco 150g-> Yogurt 150g

Tralascia tutti gli aggettivi

Nota: se come valore del dizionario hai solo un numero, riporta automaticamente la sua unit come  "pz"
Nota: Le unit non devono comparire fra parentesi


IMPORTANTE: 
ogni pasto  DEVE contenere al massimo 4 alimenti
I cibi riportati devono essere necessariamente macrocategorie alimentari differenti

non devi ripetere piu volte le verdure ma devi riportare solo "Verdure" quantità, se presenti piu di una volta

NOTA: NON FORNIRE ALTRO TESTO OLTRE AL DIZIONARIO

{context}

Question: {question}
"""

# Lista dei giorni della settimanas

def convert_to_dict_giorni(dict_lunch_temp_1):
    dict_giorni = {}
    
    for giorno, pasti in dict_lunch_temp_1.items():
        dict_giorni[giorno] = {}
        
        # Iteriamo sui pasti della giornata
        for pasto, alimenti in pasti.items():
            for alimento, info in alimenti.items():
                quantita = info['Quantità']
                dict_giorni[giorno][alimento] = dict_giorni[giorno].get(alimento, 0) + quantita
                
    return dict_giorni

# Funzione per registrare un nuovo utente
def register_user(nome, cognome, username):
    conn = sqlite3.connect('dieta.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO utenti (nome, cognome, username, dieta) VALUES (?, ?, ?, ?)", 
                  (nome, cognome, username, json.dumps({})))  # Inizializza con dieta vuota
        conn.commit()
        st.success(f"🎉 Benvenuto {nome} {cognome}! Ora puoi caricare il tuo piano nutrizionale.")
        st.session_state["username"] = username
        st.session_state["nome"] = nome
        st.session_state["cognome"] = cognome
    except sqlite3.IntegrityError:
        st.error("⚠️ Questo username è già in uso. Scegline un altro.")
    conn.close()