import streamlit as st
import pandas as pd
import datetime
import altair as alt

# --- CONFIGURAZIONE PAGINA ---
# Il tuo logo apparirà direttamente nella linguetta di Safari/Chrome
st.set_page_config(page_title="FinApp 2.0", page_icon="logo.png", layout="centered")

# ==========================================
# POP-UP (MODALS)
# ==========================================
@st.dialog("Assistente Bot 🤖")
def chatbot_modal():
    st.markdown("Chiedimi un'analisi delle tue spese o consigli sul portafoglio.")
    st.chat_message("assistant").write("Ciao! Come posso aiutarti con le tue finanze oggi?")
    msg = st.chat_input("Scrivi qui la tua domanda...")
    if msg:
        st.chat_message("user").write(msg)
        st.chat_message("assistant").write(f"*(Simulazione)* Sto analizzando il database per rispondere a: '{msg}'...")

@st.dialog("➕ Nuova Transazione")
def transazione_modal():
    with st.form("form_transazione"):
        tipo = st.selectbox("Tipo", ["Uscita", "Entrata"])
        importo = st.number_input("Importo (€)", min_value=0.0, step=0.5)
        categoria = st.selectbox("Categoria", ["Spesa", "Bollette", "Svago", "Stipendio", "Altro"])
        data = st.date_input("Data", datetime.date.today())
        if st.form_submit_button("Salva"):
            st.success("Transazione salvata! (Simulazione)")

@st.dialog("➕ Inserisci Titolo")
def titolo_modal():
    metodo = st.radio("Tipo di inserimento", ["Singolo acquisto", "Più acquisti (Prezzo Medio)"], horizontal=True)
    with st.form("form_titolo"):
        isin = st.text_input("ISIN o Ticker (es. VWCE)")
        quantita = st.number_input("Quantità", min_value=0.0, step=0.01)
        
        if metodo == "Singolo acquisto":
            prezzo = st.number_input("Prezzo di acquisto (€)", min_value=0.0, step=1.0)
            data = st.date_input("Data di acquisto", datetime.date.today())
        else:
            prezzo = st.number_input("Prezzo Medio di Carico (€)", min_value=0.0, step=1.0)
            
        if st.form_submit_button("Salva Titolo"):
            st.success("Titolo salvato nel portafoglio! (Simulazione)")

@st.dialog("➕ Nuovo PAC")
def pac_modal():
    with st.form("form_pac"):
        nome_pac = st.text_input("Nome PAC (es. ETF S&P 500)")
        importo_mensile = st.number_input("Importo Mensile Programmato (€)", min_value=0.0, step=10.0)
        giorno_mese = st.number_input("Giorno del mese per l'acquisto", min_value=1, max_value=31, step=1)
        if st.form_submit_button("Attiva PAC"):
            st.success("PAC configurato con successo! (Simulazione)")

# ==========================================
# INTESTAZIONE PRINCIPALE CON LOGO CUSTOM
# ==========================================
col_logo, col_titolo, col_bot = st.columns([0.2, 0.6, 0.2])

with col_logo:
    # Aggiriamo Streamlit forzando il browser a caricare l'immagine nativamente
    st.markdown(
        '<img src="https://raw.githubusercontent.com/postaajb/finapp/main/logo.png" style="width:100%; border-radius:15px;">', 
        unsafe_allow_html=True
    )
    
with col_titolo:
    st.title("FinApp")
    
with col_bot:
    st.write("") # Spaziatura per allineare il bottone verticalmente
    if st.button("🤖 Chat", help="Apri l'assistente IA", use_container_width=True):
        chatbot_modal()

# ==========================================
# CREAZIONE DEI 3 TAB
# ==========================================
tab1, tab2, tab3 = st.tabs(["Entrate/Uscite", "Titoli e PAC", "Storico & Modifiche"])

# ------------------------------------------
# TAB 1: ANALISI ENTRATE E USCITE
# ------------------------------------------
with tab1:
    if st.button("➕ Inserisci Transazione", use_container_width=True):
        transazione_modal()
        
    st.divider()
    
    # Dati finti per i grafici
    df_mesi = pd.DataFrame({
        "Mese": ["Gen", "Feb", "Mar", "Apr", "Mag"],
        "Entrate": [2500, 2600, 2500, 2800, 2500],
        "Uscite": [1800, 1500, 2100, 1600, 1900]
    }).set_index("Mese")

    st.subheader("Andamento Entrate vs Uscite")
    st.bar_chart(df_mesi)

    col_e, col_u = st.columns(2)
    with col_e:
        st.markdown("**Solo Entrate**")
        st.line_chart(df_mesi[["Entrate"]], color="#2ECC71") # Verde
    with col_u:
        st.markdown("**Solo Uscite**")
        st.line_chart(df_mesi[["Uscite"]], color="#E74C3C") # Rosso

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
    
    st.subheader("📈 Andamento Globale Portafoglio")
    df_portafoglio = pd.DataFrame({
        "Data": pd.date_range(start="2024-01-01", periods=5, freq="ME"),
        "Valore (€)": [10000, 10500, 10200, 11000, 11500]
    }).set_index("Data")
    st.line_chart(df_portafoglio)

    st.subheader("Dettaglio Singoli Titoli")
    df_singoli = pd.DataFrame({
        "Data": pd.date_range(start="2024-01-01", periods=5, freq="ME"),
        "VWCE": [5000, 5200, 5100, 5400, 5600],
        "BTP": [5000, 5300, 5100, 5600, 5900]
    }).set_index("Data")
    st.line_chart(df_singoli)

    # Grafici a torta con Altair
    st.divider()
    col_pie1, col_pie2 = st.columns(2)
    
    with col_pie1:
        st.markdown("**Composizione Portafoglio**")
        df_pie_port = pd.DataFrame({"Asset": ["Azioni", "Obbligazioni", "Liquidità"], "Valore": [60, 30, 10]})
        pie_chart1 = alt.Chart(df_pie_port).mark_arc(innerRadius=40).encode(
            theta="Valore", color="Asset", tooltip=["Asset", "Valore"]
        ).properties(height=250)
        st.altair_chart(pie_chart1, use_container_width=True)

    with col_pie2:
        st.markdown("**Composizione PAC**")
        df_pie_pac = pd.DataFrame({"Asset": ["S&P 500", "Emergenti", "Europa"], "Valore": [70, 15, 15]})
        pie_chart2 = alt.Chart(df_pie_pac).mark_arc(innerRadius=40).encode(
            theta="Valore", color="Asset", tooltip=["Asset", "Valore"]
        ).properties(height=250)
        st.altair_chart(pie_chart2, use_container_width=True)

# ------------------------------------------
# TAB 3: STORICO E MODIFICHE
# ------------------------------------------
with tab3:
    st.markdown("In questa sezione puoi visualizzare, **modificare** ed **esportare** i dati inseriti.")
    
    # SEZIONE TRANSAZIONI
    st.subheader("Storico Transazioni")
    df_st_transazioni = pd.DataFrame([
        {"Data": "2024-05-01", "Tipo": "Uscita", "Categoria": "Spesa", "Importo": 150.0},
        {"Data": "2024-05-02", "Tipo": "Entrata", "Categoria": "Stipendio", "Importo": 2500.0}
    ])
    # Tabella editabile
    edited_transazioni = st.data_editor(df_st_transazioni, num_rows="dynamic", use_container_width=True, key="edit_transazioni")
    
    # Bottone di Export per le Transazioni
    csv_transazioni = edited_transazioni.to_csv(index=False, sep=";").encode('utf-8')
    st.download_button(
        label="📥 Esporta Transazioni in Excel",
        data=csv_transazioni,
        file_name='storico_transazioni.csv',
        mime='text/csv'
    )
    
    st.divider()

    # SEZIONE TITOLI
    st.subheader("Storico Titoli")
    df_st_titoli = pd.DataFrame([
        {"ISIN": "IE00BK5BQT80", "Quantità": 10.5, "Prezzo Medio": 115.0},
        {"ISIN": "IT0005436693", "Quantità": 5.0, "Prezzo Medio": 98.5}
    ])
    # Tabella editabile
    edited_titoli = st.data_editor(df_st_titoli, num_rows="dynamic", use_container_width=True, key="edit_titoli")
    
    # Bottone di Export per i Titoli
    csv_titoli = edited_titoli.to_csv(index=False, sep=";").encode('utf-8')
    st.download_button(
        label="📥 Esporta Titoli in Excel",
        data=csv_titoli,
        file_name='storico_titoli.csv',
        mime='text/csv'
    )
