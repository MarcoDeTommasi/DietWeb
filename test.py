from langchain_community.chat_models import ChatOllama

#doc-intelligence like per valutare meglio pdf
#collegamento dict creato con dict lista nuova
#acquisizione utente e salvataggio in un db per memoria


llm = ChatOllama(model='llama3', temperature=0.01)


template = """Ti darò un piano alimentare personalizzato per un utente. In questo piano sono presenti le linee guida alimentari per ogni giorno della settimana e per ogni pasto.
Ti chiederò cosa è consigliato mangiare per un dato pasto in un dato giorno e tu devi rispondere elencanto i cibi e le quantità riportate.

Ogni giorno ha questi possibili pasti:

['Colazione','Spuntino','Pranzo','Cena']

NOTA: riportami 2 spuntini, uno mattutino e uno pomeridiano, 
se ti chiedo di parlare di uno spuntino e aggiungo mattutino o pomeridiano riportami rispettivamente quello fra la colazione e il pranzo e quello fra il pranzo e la cena

NOTA: riportami la risposta come una lista Python.

DEVI Rispettare questo formato, la quantità e sempre riportata:
[ 'alimento1 quantita', 'alimento2 quantita', 'alimento3 quantita']

Riporta solo il tipo di alimenti e la quatità, evita aggettivi:

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


custom_prompt = template.format(context=template, question="question")

# Inizializza il modello LLM
llm = ChatOllama(model='llama3', temperature=0.01)

# Utilizza il metodo `invoke` per interrogare il modello
messages = [
    ("system", "You are a helpful assistant. Use the given context to answer questions accurately."),
    ("human", custom_prompt)
]

response = llm.invoke(messages)
answer = response.content.strip()