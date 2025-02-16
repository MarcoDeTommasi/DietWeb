import sqlite3
import json
from datetime import datetime

# Connessione al database
conn = sqlite3.connect("dieta.db")
c = conn.cursor()

# Dati da inserire
spese = [
    ("MarcoDefault", "2024-12-15", {"Latte": {"Quantità": 100, "Unità": "ml"}, "Pane integrale": {"Quantità": 50, "Unità": "g"}, "Mela": {"Quantità": 1, "Unità": "pz"}}),
    ("MarcoDefault", "2024-12-28", {"Yogurt": {"Quantità": 300, "Unità": "g"}, "Fette biscottate": {"Quantità": 4, "Unità": "pz"}, "Mandorle": {"Quantità": 15, "Unità": "g"}}),
    ("MarcoDefault", "2025-01-05", {"Yogurt": {"Quantità": 400, "Unità": "g"},"Pasta integrale": {"Quantità": 80, "Unità": "g"}, "Pomodori": {"Quantità": 100, "Unità": "g"}, "Tonno al naturale": {"Quantità": 50, "Unità": "g"}}),
    ("MarcoDefault", "2025-01-20", {"Yogurt": {"Quantità": 100, "Unità": "g"},"Farro": {"Quantità": 70, "Unità": "g"}, "Bresaola": {"Quantità": 40, "Unità": "g"}, "Ortaggi": {"Quantità": 150, "Unità": "g"}}),
    ("MarcoDefault", "2025-01-30", {"Yogurt": {"Quantità": 600, "Unità": "g"},"Riso basmati": {"Quantità": 90, "Unità": "g"}, "Merluzzo": {"Quantità": 120, "Unità": "g"}, "Verdure miste": {"Quantità": 200, "Unità": "g"}}),
    ("MarcoDefault", "2025-02-10", {"Yogurt": {"Quantità": 250, "Unità": "g"},"Cous cous": {"Quantità": 60, "Unità": "g"}, "Fesa di tacchino": {"Quantità": 50, "Unità": "g"}, "Insalata": {"Quantità": 180, "Unità": "g"}}),
    ("MarcoDefault", "2025-02-18", {"Yogurt": {"Quantità": 300, "Unità": "g"},"Patate": {"Quantità": 150, "Unità": "g"}, "Uova": {"Quantità": 2, "Unità": "pz"}, "Zucchine": {"Quantità": 100, "Unità": "g"}}),
    ("MarcoDefault", "2025-02-25", {"Yogurt": {"Quantità": 450, "Unità": "g"},"Pane di segale": {"Quantità": 60, "Unità": "g"}, "Prosciutto cotto": {"Quantità": 40, "Unità": "g"}, "Formaggio": {"Quantità": 30, "Unità": "g"}}),
    ("MarcoDefault", "2025-03-05", {"Yogurt": {"Quantità": 450, "Unità": "g"},"Riso integrale": {"Quantità": 80, "Unità": "g"}, "Pollo": {"Quantità": 150, "Unità": "g"}, "Spinaci": {"Quantità": 120, "Unità": "g"}}),
    ("MarcoDefault", "2025-03-12", {"Yogurt": {"Quantità": 1000, "Unità": "g"},"Yogurt Greco": {"Quantità": 200, "Unità": "g"}, "Noci": {"Quantità": 10, "Unità": "g"}, "Miele": {"Quantità": 15, "Unità": "g"}})
]

# Inserimento dati nel database
for username, data, spesa in spese:
    c.execute('''
        INSERT INTO storico_spesa (username, data, lista_spesa)
        VALUES (?, ?, ?)
    ''', (username, data, json.dumps(spesa)))

# Salvataggio e chiusura
conn.commit()
conn.close()

print("✅ Dati inseriti con successo nel database!")