import streamlit as st
import pandas as pd
import datetime
import altair as alt

# --- CONNESSIONE AL DATABASE ---
@st.cache_resource
def get_db():
    try:
        import json
        from google.oauth2 import service_account
        from google.cloud import firestore
        if "firebase_key" not in st.secrets:
            return None
        # strict=False previene l'errore degli a capo nel JSON
        key_dict = json.loads(st.secrets["firebase_key"], strict=False)
        creds = service_account.Credentials.from_service_account_info(key_dict)
        db = firestore.Client(credentials=creds, project="finapp-ea8fa")
        return db
    except Exception as e:
        return None

db = get_db()

# --- FUNZIONI DI LETTURA DATI REALI ---
def get_transazioni():
    if not db: return pd.DataFrame()
    docs = db.collection("transazioni").stream()
    data = [{"ID": d.id, **d.to_dict()} for d in docs]
    return pd.DataFrame(data)

def get_titoli():
    if not db: return pd.DataFrame()
    docs = db.collection("titoli").stream()
    data = [{"ID": d.id, **d.to_dict()} for d in docs]
    return pd.DataFrame(data)

def get_pac():
    if not db: return pd.DataFrame()
    docs = db.collection("pac").stream()
    data = [{"ID": d.id, **d.to_dict()} for d in docs]
    return pd.DataFrame(data)

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(
    page_title="FinApp 2.0", 
    page_icon="https://raw.githubusercontent.com/postaajb/finapp/main/IMG_8037.png", 
    layout="centered"
)

# ==========================================
# POP-UP E MODALS
# ==========================================
@st.dialog("Assistente Bot 🤖")
def chatbot_modal():
    st.markdown("Sono la tua **IA Finanziaria basata su Google Gemini**. Conosco il tuo database, chiedimi analisi avanzate, consigli o riassunti!")
    
    df_t = get_transazioni()
    df_tit = get_titoli()
    
    msg = st.chat_input("Es. 'In quale categoria ho speso di più?' o 'Riassumi il mio portafoglio'")
    if msg:
        st.chat_message("user").write(msg)
        
        try:
            import google.generativeai as genai
            
            if "gemini_key" not in st.secrets:
                st.chat_message("assistant").error("⚠️ Manca la chiave API di Gemini nei Secret.")
            else:
                genai.configure(api_key=st.secrets["gemini_key"])
                
                # Usiamo direttamente l'identificativo standard aggiornato (senza auto-rilevamento)
                model = genai.GenerativeModel("gemini-2.5-flash")
                
                # Creiamo il "Contesto" per l'IA
                dati_transazioni = df_t.to_dict('records') if not df_t.empty else 'Nessuna transazione registrata.'
                dati_titoli = df_tit.to_dict('records') if not df_tit.empty else 'Nessun titolo in portafoglio.'
                
                prompt_di_sistema = f"""
                Sei un assistente finanziario personale empatico, professionale e conciso. 
                Rispondi SEMPRE in italiano, usando grassetti ed elenchi puntati per facilitare la lettura.
                Usa QUESTI DATI che rappresentano il database attuale dell'utente per rispondere in modo preciso:
                
                TRANSAZIONI DELL'UTENTE: {dati_transazioni}
                PORTAFOGLIO TITOLI DELL'UTENTE: {dati_titoli}
                
                Domanda dell'utente a cui rispondere: "{msg}"
                """
                
                # Chiamata all'Intelligenza Artificiale
                with st.spinner("Gemini sta analizzando i tuoi dati..."):
                    response = model.generate_content(prompt_di_sistema)
                    st.chat_message("assistant").write(response.text)
                    
        except Exception as e:
            st.chat_message("assistant").error(f"Errore tecnico Gemini: {e}")

@st.dialog("➕ Nuova Transazione")
def transazione_modal():
    with st.form("form_transazione"):
        tipo = st.selectbox("Tipo", ["Uscita", "Entrata"])
        importo = st.number_input("Importo (€)", min_value=0.0, step=0.5)
        categoria = st.selectbox("Categoria", ["Spesa", "Bollette", "Svago", "Stipendio", "Altro"])
        data = st.date_input("Data", datetime.date.today())
        
        if st.form_submit_button("Salva nel Database"):
            if db:
                db.collection("transazioni").document().set({
                    "tipo": tipo, "importo": float(importo), "categoria": categoria, "data": str(data)
                })
                st.success("✅ Salvata! Chiudi e ricarica la pagina per vederla.")
            else:
                st.warning("⚠️ Database non collegato.")

@st.dialog("➕ Inserisci Titolo")
def titolo_modal():
    metodo = st.radio("Tipo di inserimento", ["Singolo acquisto", "Più acquisti (Prezzo Medio)"], horizontal=True)
    with st.form("form_titolo"):
        isin = st.text_input("ISIN o Ticker (es. VWCE)")
        quantita = st.number_input("Quantità", min_value=0.0, step=0.01)
        prezzo = st.number_input("Prezzo (€)", min_value=0.0, step=1.0)
        
        if st.form_submit_button("Salva nel Portafoglio"):
            if db and isin:
                db.collection("titoli").document().set({
                    "isin": isin.upper(), "quantita": float(quantita), "prezzo": float(prezzo), "metodo": metodo
                })
                st.success("✅ Titolo salvato in Cloud! Ricarica la pagina.")

@st.dialog("➕ Nuovo PAC")
def pac_modal():
    with st.form("form_pac"):
        nome_pac = st.text_input("Nome PAC (es. ETF S&P 500)")
        importo_mensile = st.number_input("Importo Mensile (€)", min_value=0.0, step=10.0)
        giorno = st.number_input("Giorno del mese", min_value=1, max_value=31, step=1)
        if st.form_submit_button("Attiva PAC"):
            if db and nome_pac:
                db.collection("pac").document().set({
                    "nome": nome_pac.upper(), "importo_mensile": float(importo_mensile), "giorno": giorno
                })
                st.success("✅ PAC configurato in Cloud! Ricarica la pagina.")

@st.dialog("🔍 Dettaglio Composizione")
def dettaglio_portafoglio_modal():
    st.markdown("Dettaglio Analitico dei tuoi investimenti:")
    df_tit = get_titoli()
    if not df_tit.empty:
        df_tit['Valore'] = df_tit['quantita'] * df_tit['prezzo']
        for index, row in df_tit.iterrows():
            st.write(f"📈 **{row['isin']}**: {row['Valore']:,.2f} € (Qt: {row['quantita']} a {row['prezzo']}€)")
    else:
        st.write("Nessun titolo presente.")

# ==========================================
# INTESTAZIONE PRINCIPALE
# ==========================================
col_logo, col_titolo, col_bot = st.columns([0.15, 0.65, 0.2])

with col_logo:
    st.markdown(
        '<img src="https://raw.githubusercontent.com/postaajb/finapp/main/IMG_8037.png" style="max-width: 55px; width:100%; border-radius:12px; margin-top:5px;">', 
        unsafe_allow_html=True
    )
    
with col_titolo:
    st.title("FinApp")
    
with col_bot:
    st.write("") 
    if st.button("💬 Bot", use_container_width=True):
        chatbot_modal()

# Lettura di tutti i dati per popolare l'app
df_transazioni = get_transazioni()
df_titoli = get_titoli()
df_pac = get_pac()

# ==========================================
# TABELLONI E GRAFICI
# ==========================================
tab1, tab2, tab3 = st.tabs(["Entrate/Uscite", "Titoli e PAC", "Storico & Modifiche"])

# ------------------------------------------
# TAB 1: ENTRATE E USCITE
# ------------------------------------------
with tab1:
    if st.button("➕ Inserisci Transazione", use_container_width=True):
        transazione_modal()
    st.divider()
    
    if df_transazioni.empty:
        st.info("📊 Nessuna transazione. Clicca su (+) per inserire la tua prima spesa o entrata.")
    else:
        # Preparazione dati reali per il grafico a barre
        df_t = df_transazioni.copy()
        df_t['data'] = pd.to_datetime(df_t['data'])
        df_t['Mese'] = df_t['data'].dt.strftime('%Y-%m')
        df_group = df_t.groupby(['Mese', 'tipo'])['importo'].sum().unstack().fillna(0)
        
        if 'Entrata' not in df_group: df_group['Entrata'] = 0
        if 'Uscita' not in df_group: df_group['Uscita'] = 0
            
        st.subheader("Andamento Mese per Mese")
        st.bar_chart(df_group)

        # Grafici singoli (Entrate vs Uscite)
        col_e, col_u = st.columns(2)
        with col_e:
            st.markdown("**Solo Entrate**")
            st.line_chart(df_group['Entrata'], color="#2ECC71")
        with col_u:
            st.markdown("**Solo Uscite**")
            st.line_chart(df_group['Uscita'], color="#E74C3C")

# ------------------------------------------
# TAB 2: TITOLI E PAC
# ------------------------------------------
with tab2:
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        if st.button("➕ Inserisci Titolo", use_container_width=True):
            titolo_modal()
    with col_t2:
        if st.button("➕ Nuovo PAC", use_container_width=True):
            pac_modal()
    st.divider()
    
    st.subheader("📈 Andamento Portafoglio")
    # Andamento finto per mantenere il design finché non creiamo uno storico temporale dei titoli
    df_andamento_simulato = pd.DataFrame({
        "Data": pd.date_range(start="2024-01-01", periods=5, freq="ME"),
        "Valore Stimato (€)": [10000, 10500, 10200, 11000, 11500]
    }).set_index("Data")
    st.line_chart(df_andamento_simulato)

    st.divider()
    
    # DUE TORTE AFFIANCATE RIPRISTINATE
    col_pie1, col_pie2 = st.columns(2)
    
    with col_pie1:
        st.markdown("**Composizione Portafoglio**")
        if not df_titoli.empty:
            df_titoli['Valore'] = df_titoli['quantita'] * df_titoli['prezzo']
            pie_chart1 = alt.Chart(df_titoli).mark_arc(innerRadius=40).encode(
                theta="Valore", color="isin", tooltip=["isin", "Valore"]
            ).properties(height=250)
            st.altair_chart(pie_chart1, use_container_width=True)
        else:
            st.write("Nessun titolo.")

    with col_pie2:
        st.markdown("**Composizione PAC**")
        if not df_pac.empty:
            pie_chart2 = alt.Chart(df_pac).mark_arc(innerRadius=40).encode(
                theta="importo_mensile", color="nome", tooltip=["nome", "importo_mensile"]
            ).properties(height=250)
            st.altair_chart(pie_chart2, use_container_width=True)
        else:
            st.write("Nessun PAC attivo.")
    
    if st.button("🔍 Apri Dettaglio Titoli", use_container_width=True):
        dettaglio_portafoglio_modal()

# ------------------------------------------
# TAB 3: STORICO E MODIFICHE (TABELLE EDITABILI)
# ------------------------------------------
with tab3:
    st.markdown("Usa le tabelle sottostanti per modificare i dati prima di esportarli.")
    
    st.subheader("Storico Transazioni")
    if not df_transazioni.empty:
        # Tabella editabile mantenuta come da richiesta originaria
        edited_transazioni = st.data_editor(df_transazioni.drop(columns=["ID"], errors='ignore'), num_rows="dynamic", use_container_width=True)
        csv_t = edited_transazioni.to_csv(index=False, sep=";").encode('utf-8')
        st.download_button("📥 Esporta Transazioni (Excel/CSV)", data=csv_t, file_name='transazioni.csv')
    else:
        st.write("Nessuna transazione registrata.")
        
    st.divider()
    
    st.subheader("Storico Titoli")
    if not df_titoli.empty:
        edited_titoli = st.data_editor(df_titoli.drop(columns=["ID"], errors='ignore'), num_rows="dynamic", use_container_width=True)
        csv_tit = edited_titoli.to_csv(index=False, sep=";").encode('utf-8')
        st.download_button("📥 Esporta Titoli (Excel/CSV)", data=csv_tit, file_name='titoli.csv')
    else:
        st.write("Nessun titolo registrato.")
