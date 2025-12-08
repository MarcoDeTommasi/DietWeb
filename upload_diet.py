
import fitz
import json
from utils import query_llm
import re

def split_text_with_overlap(text, chunk_size=500, overlap=100):
    """
    Suddivide il testo in chunk con sovrapposizione.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap  # Avanza con sovrapposizione
    return chunks

def extract_food_list(chunks):
    """
    Usa un LLM per estrarre gli alimenti presenti nel piano alimentare inserito
    """
    food_list = []

    for i, chunk in enumerate(chunks):
        # Prompt per estrarre i giorni
        prompt = f"""
        Questo è una parte del testo di una dieta. Il tuo compito e' estrarre TUTTI i cibi menzionati in questo testo.
        restituisci un array degli alimenti presenti SENZA duplicati.
        Riporta i cibi tutti in minuscolo, senza accenti e con _ al posto degli spazi.
        La tua risposta deve essere SOLO L'ARRAY.
        Testo: 
        {chunk}
        """
        try:
            response = query_llm(prompt)

            match = re.search(r"\[.*?\]", response, re.DOTALL)
            if match:
                json_array = match.group(0)  # Estrai solo l'array JSON
                parsed_response = json.loads(json_array)
                food_list.extend(parsed_response)  # Usa extend per aggiungere gli elementi
            else:
                print(f"Errore: nessun array JSON trovato nella risposta. Risposta: {response}")
        except json.JSONDecodeError:
            print(f"Errore: la risposta non è un JSON valido. Risposta: {response}")    
        except Exception as e:
            print(f"Errore durante l'elaborazione del chunk {i+1}: {e}")

    return list(set(food_list))

def get_food_list_from_pdf(pdf_file):
    """
    Legge un file PDF, estrae il testo e processa la dieta con un LLM.
    """
    # Step 1: Estrai il testo dal PDF
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    # Step 2: Suddividi il testo in chunk con sovrapposizione
    chunks = split_text_with_overlap(text, chunk_size=300, overlap=100)

    # Step 3: Chunking semantico per estrarre i giorni
    food_list = extract_food_list(chunks)

    if len(food_list) == 0 or food_list is None:
        print("Nessun alimento estratto dal piano alimentare.")
        food_list = []
    
    return food_list

def create_conversion_dict(food_list):
    """
    Crea un dizionario che converte alimenti codificati in alimenti leggibili.
    
    Args:
        food_list (list): Lista di alimenti codificati (es. ["pane_integrale", "yogurt_greco"]).
    
    Returns:
        dict: Dizionario con alimenti codificati come chiavi e versioni leggibili come valori.
    """
    conversion_dict = {}
    for food in food_list:
        # Sostituisci "_" con spazi e metti in formato Title Case
        readable_food = food.replace("_", " ").title()
        conversion_dict[food] = readable_food
    return conversion_dict

def convert_quantities_to_int(d):
    for key, value in d.items():
        if isinstance(value, dict):
            convert_quantities_to_int(value)  # Ricorsione per scendere nei sotto-dizionari
        elif key == "Quantità" and isinstance(value, float) and value.is_integer():
            d[key] = int(value)  # Conversione a intero solo se non ci sono decimali
    return d

