# DietApp

Applicazione Streamlit per gestire un piano alimentare, calcolare la lista della
spesa in base alla dispensa e analizzare lo storico degli acquisti.

## Avvio locale

1. Crea e attiva un ambiente Python 3.11.
2. Installa le dipendenze: `pip install -r requirements.txt`.
3. Copia `.env.example` in `.env` e compila solo le variabili necessarie.
4. Avvia: `streamlit run app.py`.

Senza `DATABASE_URL` l'app usa `dieta.db` nella root del progetto. Le tabelle
vengono create automaticamente, ma non vengono creati utenti demo.

## Struttura

- `app.py`: autenticazione e registrazione.
- `pages/`: pagine Streamlit, limitate alla presentazione e all'orchestrazione.
- `dietapp/`: configurazione, database, sicurezza, repository e logica di dominio.
- `scripts/`: utility amministrative esplicite.
- `tests/`: test della logica, analytics e persistenza.

Per il deploy e la migrazione del database consulta [DEPLOYMENT.md](DEPLOYMENT.md).

## Verifiche

```text
python -m unittest discover -s tests -v
ruff check .
```

Non committare `.env`, database locali o PDF delle diete: possono contenere
credenziali o dati personali.
