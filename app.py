import streamlit as st
from google.cloud import firestore
import pandas as pd
import datetime

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="FinApp 2.0", page_icon="📊", layout="centered")

# --- CONNESSIONE AL DATABASE ---
# Utilizzeremo i Secret di Streamlit per accedere in modo sicuro (lo configuriamo al prossimo step)
@st.cache_resource
def get_db():
    try:
        # Quando configureremo i secret, Streamlit capirà in automatico come collegarsi
        db = firestore.Client(project="finapp-ea8fa")
        return db
    except Exception as e:
        return None

db = get_db()

st.title("📊 La mia FinApp 2.0")

if not db:
    st.error("⚠️ In attesa della Chiave Segreta di Google per accedere ai dati...")

# --- CREAZIONE DEI TAB (MENU) ---
tab1, tab2, tab3, tab4 = st.tabs(["💸 Transazioni", "📈 Titoli & PAC", "📊 Grafici", "🤖 Bot"])

# ==========================================
# TAB 1: TRANSAZIONI QUOTIDIANE
# ==========================================
with tab1:
    st.header("Nuova Transazione")
    with st.form("form_transazione", clear_on_submit=True):
        tipo = st.selectbox("Tipo", ["Uscita", "Entrata"])
        importo = st.number_input("Importo (€)", min_value=0.0, step=0.5)
        categoria = st.selectbox("Categoria", ["Spesa", "Bollette", "Svago", "Stipendio", "Altro"])
        nota = st.text_input("Nota (opzionale)")
        data = st.date_input("Data", datetime.date.today())
        
        submit_transazione = st.form_submit_button("Salva Transazione")
        if submit_transazione and db:
            doc_ref = db.collection("transazioni").document()
            doc_ref.set({
                "tipo": tipo,
                "importo": importo,
                "categoria": categoria,
                "nota": nota,
                "data": str(data),
                "timestamp": firestore.SERVER_TIMESTAMP
            })
            st.success("✅ Transazione salvata nel Cloud!")

# ==========================================
# TAB 2: TITOLI E PAC (Piano Accumulo)
# ==========================================
with tab2:
    st.header("Gestione Investimenti")
    with st.expander("➕ Inserisci nuovo acquisto Titolo/PAC", expanded=True):
        with st.form("form_pac", clear_on_submit=True):
            nome_titolo = st.text_input("Nome Titolo o ETF (es. VWCE)")
            quota = st.number_input("Quote Acquistate", min_value=0.0, step=0.01)
            prezzo = st.number_input("Prezzo per quota (€)", min_value=0.0, step=1.0)
            data_pac = st.date_input("Data Acquisto", datetime.date.today())
            
            submit_pac = st.form_submit_button("Salva nel PAC")
            if submit_pac and db and nome_titolo:
                db.collection("investimenti").document().set({
                    "titolo": nome_titolo.upper(),
                    "quote": quota,
                    "prezzo_acquisto": prezzo,
                    "totale_investito": quota * prezzo,
                    "data": str(data_pac),
                })
                st.success(f"✅ Acquisto di {nome_titolo} registrato!")

# ==========================================
# TAB 3: GRAFICI E DASHBOARD
# ==========================================
with tab3:
    st.header("Andamento Finanze")
    if db:
        st.write("Qui appariranno i tuoi grafici aggiornati in tempo reale (verranno attivati non appena inseriremo i primi dati reali).")
        # Placeholder visivo per il grafico
        chart_data = pd.DataFrame(
            {"Entrate": [0, 1500, 200, 0, 50], "Uscite": [50, 100, 400, 50, 120]}, 
            index=["Lun", "Mar", "Mer", "Gio", "Ven"]
        )
        st.bar_chart(chart_data)
    else:
        st.warning("Collega il database per vedere le statistiche.")

# ==========================================
# TAB 4: ASSISTENTE BOT
# ==========================================
with tab4:
    st.header("Assistente AI")
    st.markdown("Chiedi al bot un riassunto delle tue spese o un consiglio sul budget.")
    
    msg = st.chat_input("Es: 'Quanto ho speso in Svago questo mese?'")
    if msg:
        st.chat_message("user").write(msg)
        # Qui in futuro collegheremo le API di OpenAI/Google per le risposte intelligenti
        st.chat_message("assistant").write(f"Ho ricevuto la tua richiesta: '{msg}'. (Sto analizzando il tuo database Firestore...)")
