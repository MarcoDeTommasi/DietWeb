# Deploy consigliato

## Scelta a costo zero

Per una demo o un progetto personale a traffico ridotto:

- **app:** Render Web Service Free;
- **database:** Neon Postgres Free;
- **API AI:** OpenRouter, con budget/limiti configurati sul relativo account.

Render resta adatto per il processo Streamlit, ma il database gratuito di Render
scade dopo 30 giorni. Inoltre il filesystem del web service è effimero: non usare
`dieta.db` online. Neon non ha quel limite temporale e fornisce una connection
string PostgreSQL compatibile con `DATABASE_URL`.

Il piano gratuito non è una configurazione production-grade: il web service va
in sleep dopo inattività, il primo accesso può essere lento e non ci sono SLA.

## Render + Neon

1. Crea un progetto Neon nella stessa area geografica scelta per Render.
2. Copia la connection string PostgreSQL di Neon, preferibilmente quella pooled.
3. In Render scegli **New → Blueprint** e collega questo repository. Render userà
   `render.yaml`.
4. Imposta il secret `DATABASE_URL` con la connection string Neon.
5. Imposta `OPENROUTER_API_KEY` se vuoi abilitare l'import da PDF.
6. Avvia il deploy e verifica `/_stcore/health`.

L'app converte automaticamente URL `postgres://` e `postgresql://` nel formato
richiesto da SQLAlchemy/psycopg2 e crea le tabelle mancanti all'avvio.

## Migrare il database SQLite esistente

Esegui prima un backup di `dieta.db`. Poi, dalla root del progetto:

```text
python -m scripts.migrate_sqlite_to_postgres dieta.db --target-url "postgresql://..."
```

Lo script non cancella dati e salta gli utenti già presenti. Le password legacy
in chiaro vengono trasformate in hash bcrypt durante migrazione o avvio.

## Alternative

- **Supabase Free:** più funzionalità integrate, 500 MB di database; il progetto
  può essere messo in pausa dopo una settimana di inattività.
- **Render Postgres paid:** la scelta più semplice se vuoi rete privata e un solo
  fornitore; evita la scadenza del database Free.
- **Render web paid + Postgres paid:** scelta minima per un servizio realmente
  pubblico, senza cold start e con persistenza/supporto più affidabili.

Prima di trattare dati sanitari reali, definisci consenso, retention, cancellazione
account/dati, backup, informativa privacy e requisiti GDPR con un professionista.
