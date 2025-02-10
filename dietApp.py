import os
import random
import pandas as pd
import streamlit as st
import numpy as np
from datetime import datetime


dict_giorni={
'Lunedì':{
    'Fagioli':80,
    'Verdure':400,
    'Frutta':2,
    'Piadine':55,
    'Fesa':50,
    'Merluzzo':200,
    'Ortaggi':100,
    'Marmellata':40,
    'Latte':200,
    'Fette_Biscottate':50,
    'Frutta_Secca':4,
    'Pane':50,
    'Pasta':60},
'Martedì':{
    'Verdure':400,
    'Frutta':4,
    'Piadine':55,
    'Frutta_Secca':5,
    'Pane':50,
    'Cereali':50,
    'Farro':70,
    'Pomodori':20,
    'Yogurt':170,
    'Pollo':200,
    'Uova':2},
'Mercoledì':{
    'Verdure':400,
    'Frutta':3,
    'Piadine':55,
    'Ortaggi':100,
    'Marmellata':50,
    'Pane':100,
    'Prosciutto':40,
    'Succo_di_Frutta':200,
    'Cous_Cous':70,
    'Tonno':120,
    'Ricotta':120
 },
'Giovedì':{
 'Verdure':400,
 'Frutta':3,
 'Piadine':55,
 'Fesa':150,
 'Merluzzo':200,
 'Ortaggi':100,
 'Marmellata':50,
 'Frutta_Secca':5,
 'Pane':50,
 'Pomodori':20,
 'Yogurt':170,
 'Biscotti':50,
 'Patate':300,
},
'Venerdì':{
 'Fagioli':50,
 'Latte':200,
 'Verdure':400,
 'Frutta':3,
 'Piadine':55,
 'Fesa':50,
 'Ortaggi':100,
 'Marmellata':40,
 'Fette_Biscottate':50,
 'Frutta_Secca':9,
 'Pane':50,
 'Pomodori':20,
 'Uova':2,
 'Pasta':60,

},
'Sabato':{
 'Yogurt':170,
 'Verdure':200,
 'Cereali':50,
 'Frutta':1,
 'Piadine':55,
 'Ortaggi':100,
 'Fette_Biscottate':50,
 'Frutta_Secca':9,
 'Pane':60,
 'Pollo':220,
 'Yogurt':125
},
'Domenica':{
 'Succo_di_Frutta':200,
 'Verdure':400,
 'Prosciutto':40,
 'Frutta':2,
 'Piadine':55,
 'Ortaggi':100,
 'Pane':50,
 'Yogurt':125,
 'Pasta':80,
 'Filetto':150,
 'Salmone':100}
 }

dict_lunch={

'Lunedì':{
    'Colazione':{
    'Marmellata':40,
    'Latte':200,
    'Fette_Biscottate':50,

    },
    'Pranzo':{
    'Fagioli':80,
    'Verdure':200,
    'Pane':60,
    'Frutta':1
    },
    'Cena':{
        'Verdure':200,
        'Piadine':55,
        'Merluzzo':200,
        'Ortaggi':100,
        'Frutta':1
    },
    'SpuntinoMattina':{
        'Frutta':1,
        'Frutta_Secca':4
    },
    'SpuntinoPomeriggio':{
        'Pane':50,
        'Fesa':50
    }
},
'Martedì':{
    'Colazione':{
    'Yogurt':170,
    'Cereali':50,
    'Frutta':1

    },
    'Pranzo':{
    'Farro':70,
    'Verdure':200,
    'Uova':2,
    'Frutta':1
    },
    'Cena':{
        'Verdure':200,
        'Piadine':55,
        'Pollo':200,
        'Ortaggi':100,
        'Frutta':1
    },
    'SpuntinoMattina':{
        'Frutta_Secca':4,
        'Frutta':1
    },
    'SpuntinoPomeriggio':{
        'Pane':50,
        'Pomodori':50
    }
},
'Mercoledì':{
       'Colazione':{
    'Succo_di_Frutta':200,
    'Pane':50,
    'Prosciutto':40

    },
    'Pranzo':{
    'Cous_Cous':70,
    'Verdure':200,
    'Tonno':120,
    'Frutta':1
    },
    'Cena':{
        'Verdure':200,
        'Piadine':55,
        'Ricotta':120,
        'Ortaggi':100,
        'Frutta':1
    },
    'SpuntinoMattina':{
        'Frutta':1
    },
    'SpuntinoPomeriggio':{
        'Pane':50,
        'Pomodori':50
    }
 },
'Giovedì':{
          'Colazione':{
    'Yogurt':170,
    'Biscotti':50,
    'Marmellata':50

    },
    'Pranzo':{
    'Patate':300,
    'Verdure':200,
    'Merluzzo':200,
    'Frutta':1
    },
    'Cena':{
        'Verdure':200,
        'Piadine':55,
        'Bresaola':100,
        'Ortaggi':100,
        'Frutta':1
    },
    'SpuntinoMattina':{
        'Frutta':1,
        'Frutta_Secca':4
    },
    'SpuntinoPomeriggio':{
        'Pane':50,
        'Pomodori':50
    }
},
'Venerdì':{
    'Colazione':{
    'Latte':200,
    'Fette_Biscottate':50,
    'Marmellata':40

    },
    'Pranzo':{
    'Pasta':60,
    'Fesa':50,
    'Verdure':200,
    'Fagioli':50,
    'Frutta':1
    },
    'Cena':{
        'Verdure':200,
        'Piadine':55,
        'Uova':2,
        'Ortaggi':100,
        'Frutta':1
    },
    'SpuntinoMattina':{
        'Frutta':1,
        'Frutta_Secca':9
    },
    'SpuntinoPomeriggio':{
        'Pane':50,
        'Pomodori':50
    }
},
'Sabato':{
    'Colazione':{
    'Yogurt':170,
    'Cereali':50,
    'Frutta':1

    },
    'Pranzo':{
    'Pollo':220,
    'Verdure':200,
    'Pane':60,
    },
    'Cena':{
        'Verdure':200,
        'Piadine':55,
        'Ricotta':120,
        'Ortaggi':100,
        'Frutta':1
    },
    'SpuntinoMattina':{
        'Frutta_Secca':9
    },
    'SpuntinoPomeriggio':{
        'Yogurt':125
    }
},
'Domenica':{

    'Colazione':{
    'Succo_di_Frutta':200,
    'Pane':50,
    'Prosciutto':40

    },
    'Pranzo':{
    'Filetto':150,
    'Verdure':200,
    'Pasta':80,
    'Frutta':1
    },
    'Cena':{
        'Verdure':200,
        'Piadine':55,
        'Salmone':120,
        'Ortaggi':100,
        'Frutta':1
    },
    'SpuntinoMattina':{
        'Yogurt':125
    },
    'SpuntinoPomeriggio':{
        'Pane':50,
        'Pomodori':50
    }
    }
}


giorni_map = {
    "Monday": "Lunedì",
    "Tuesday": "Martedì",
    "Wednesday": "Mercoledì",
    "Thursday": "Giovedì",
    "Friday": "Venerdì",
    "Saturday": "Sabato",
    "Sunday": "Domenica"}

def cibo_settimana_da_Acquistare(food_you_have,food_required):
    elementi_da_comprare={}
    for food in food_required.keys():
      if food in food_you_have.keys():
        elementi_da_comprare[food]=food_required[food]-food_you_have[food]
      else:
       elementi_da_comprare[food]=food_required[food]
    return elementi_da_comprare

def Output_lista_settimana(dict_elementi,list_of_days):
    #questa funzione prima risolve i giorni, quindi ottiene un dizionario che è sola funzione degli alimenti
    #poi la passa alla funzione "cibo settiamana da acquistare" e si va a calcolare l'output effettivo di cibo da
    #comprare
    dict_output={}
    for giorni in list_of_days:
        for alimento in dict_giorni[giorni]:
            if alimento in list(dict_output.keys()):
                dict_output[alimento]+=dict_giorni[giorni][alimento]
            else:
                dict_output[alimento]= dict_giorni[giorni][alimento]

    elementi_da_comprare=cibo_settimana_da_Acquistare(dict_elementi,dict_output)
    return_dict=elementi_da_comprare.copy()
    for key in elementi_da_comprare.keys():
        if elementi_da_comprare[key]<=0:
            del return_dict[key]


    return return_dict

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

# Set page centered
st.set_page_config(layout="wide")



def get_food_emoji(food_name):
    # Dizionario che associa ogni tipo di cibo a un'emoji
    emoji_map = {
        "Fagioli": "🫘",
        "Verdure": "🥦",
        "Frutta": "🍎",
        "Piadine": "🌮",
        "Fesa": "🍗",
        "Merluzzo": "🐟",
        "Ortaggi": "🥕",
        "Marmellata": "🍯",
        "Latte": "🥛",
        "Fette Biscottate": "🍞",
        "Frutta Secca": "🥜",
        "Pane": "🍞",
        "Pasta": "🍝",
        "Cereali": "🥣",
        "Farro": "🌾",
        "Pomodori": "🍅",
        "Yogurt": "🍶",
        "Pollo": "🍗",
        "Uova": "🥚",
        "Prosciutto": "🥓",
        "Succo di Frutta": "🧃",
        "Cous Cous": "🍛",
        "Tonno": "🐟",
        "Ricotta": "🧀",
        "Biscotti": "🍪",
        "Patate": "🥔",
        "Filetto": "🥩",
        "Salmone": "🐟"
    }
    # Rimuove gli underscore e aggiunge l'emoji
    readable_name = food_name.replace("_", " ")
    emoji = emoji_map.get(readable_name, "🍴")  # Usa "🍴" come emoji predefinita
    return f"{emoji}"

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
    # Ottieni l'orario corrente
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
    cibi_suggeriti = pasti_del_giorno.get(pasto_corrente, [])

    # Costruisci il messaggio con emoji
    if cibi_suggeriti:
        messaggio = f"Prossimo pasto {pasto_corrente.replace('_', ' ').capitalize()}:\n"
        for alimento in cibi_suggeriti:
            emoji = get_food_emoji(alimento)
            quantity = get_food_unit(alimento)
            messaggio += f"- {emoji} {alimento.replace('_', ' ')} : {dict_lunch[giorno_italiano][pasto_corrente][alimento]} {quantity}\n"
    else:
        messaggio = "Non ci sono suggerimenti disponibili per il tuo pasto attuale."

    return messaggio

# Funzione principale
def main():
    st.title("DietApp Web Version!")
    st.write("Benvenuta/o! Questa applicazione ha diverse funzioni:")
    
    # Sezione per suggerimenti pasto
    st.subheader("🍽️ Suggerimento per il prossimo pasto")
    messaggio_pasto = suggerisci_pasto()
    st.write(messaggio_pasto)

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

        for giorno in giorni_selezionati:
            for alimento, quantita in dict_giorni.get(giorno, {}).items():
                dict_max_elements[alimento] = dict_max_elements.get(alimento, 0) + quantita

        # Crea slider per ogni alimento con emoji e unità di misura
        for alimento, max_quantita in dict_max_elements.items():
            emoji_name = get_food_emoji(alimento)
            unit = get_food_unit(alimento)
            dict_to_fill[alimento] = st.slider(
                f"{emoji_name} {alimento.replace('_', ' ')} (max: {max_quantita} {unit})",
                min_value=0,
                max_value=max_quantita,
                value=max_quantita // 2,
                step=10,
                key=f"slider_{alimento}"
            )

    # Bottone per calcolare la lista della spesa
    if st.button("✔️ Submit List"):
        lista_spesa = {k: v for k, v in dict_to_fill.items() if v > 0}
        st.session_state["lista_spesa"] = lista_spesa

        # Recupera la lista della spesa dallo stato della sessione
        lista_spesa = st.session_state.get("lista_spesa", {})

        # Mostra la lista della spesa interattiva
        st.subheader("🛒 Lista della spesa interattiva:")
        if len(lista_spesa) > 0:
            col1, col2 = st.columns(2)
            chiavi_eliminati = []

            # Cicla sugli elementi della lista e mostra in due colonne
            for i, (alimento, quantita) in enumerate(lista_spesa.items()):
                col = col1 if i % 2 == 0 else col2
                emoji_name = get_food_emoji(alimento)
                unit = get_food_unit(alimento)

                with col:
                    if st.checkbox(f"{emoji_name} {alimento.replace('_', ' ')}: {quantita} {unit}", key=f"check_{alimento}"):
                        chiavi_eliminati.append(alimento)

            # Rimuove gli elementi selezionati
            for chiave in chiavi_eliminati:
                del lista_spesa[chiave]

            st.session_state["lista_spesa"] = lista_spesa

            if len(lista_spesa) == 0:
                st.success("🎉 Hai completato tutta la lista della spesa!")
        else:
            st.success("🎉 Hai già tutto il necessario in dispensa!")
    
    st.divider()

    # Seconda espansione: Analitiche
    with st.expander("2. Analitiche consumi ed utilizzo", expanded=False):
        st.write("Qui puoi vedere analitiche avanzate!")


if __name__ == "__main__":
    main()