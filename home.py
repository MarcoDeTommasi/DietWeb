from datetime import datetime
from utils import get_food_emoji
from upload_diet import create_conversion_dict

def determina_pasto_corrente():
    ora_corrente = datetime.now().hour
    if ora_corrente < 11:
        return "Colazione"
    elif 11 <= ora_corrente < 16:
        return "Pranzo"
    else:
        return "Cena"

def suggerisci_pasti(dict_lunch, giorno, pasti_selezionati, food_list,  include_spuntini=False):
    conversion_dict = create_conversion_dict(food_list)
        
    pasti_del_giorno = dict_lunch.get(giorno, {})
    pasti_principali = ""
    spuntini = ""
    
    for pasto, cibi in pasti_del_giorno.items():
        if pasto in ["Colazione", "Pranzo", "Cena"] and pasto in pasti_selezionati:
            pasti_principali += f"### {pasto.replace('_', ' ').capitalize()}\n"
            for alimento, info in cibi.items():
                emoji = get_food_emoji(alimento)
                alimento = conversion_dict.get(alimento, alimento)
                quantity = info['Quantità']
                unit = info['Unità']
                pasti_principali += f"- {emoji} {alimento.replace('_', ' ')}: {quantity} {unit}\n"
            pasti_principali += "\n"
        elif "Spuntino" in pasto:
            spuntini += f"###  Spuntino {pasto.replace('Spuntino', '').capitalize()}\n"
            for alimento, info in cibi.items():
                emoji = get_food_emoji(alimento)
                alimento = conversion_dict.get(alimento, alimento)
                quantity = info['Quantità']
                unit = info['Unità']
                spuntini += f"- {emoji} {alimento.replace('_', ' ')}: {quantity} {unit}\n"
            spuntini += "\n"
    
    return pasti_principali, spuntini
