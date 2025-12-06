import sqlite3

def elimina_nicola():
    try:
        conn = sqlite3.connect('dieta.db')
        c = conn.cursor()

        # Elimina l'utente Nicola
        c.execute("DELETE FROM utenti WHERE username = ?", ('nicoladefault',))

        conn.commit()
        print("✅ Utente 'nicoladefault' eliminato con successo.")

    except sqlite3.Error as e:
        print(f"❌ Errore durante l'eliminazione di Nicola: {e}")

    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    elimina_nicola()
