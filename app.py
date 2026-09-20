import streamlit as st
from google.cloud import firestore

# Configurazione pagina per iPhone
st.set_page_config(page_title="FinApp 2.0", page_icon="📊", layout="centered")

# Inizializza il database Cloud (Non servono password qui, Google riconosce il server automaticamente!)
try:
    db = firestore.Client(project="finapp-ea8fa")
    db_status = "✅ Connesso a Firestore"
except Exception as e:
    db_status = f"❌ Errore DB: {e}"

st.title("FinApp 2.0")
st.write("Benvenuto nel tuo server privato Google Cloud Run!")
st.info(db_status)

# Form di test per il database
st.subheader("Test Inserimento Dati")
importo = st.number_input("Importo (€)", value=0.0, step=1.0)
causale = st.text_input("Causale")

if st.button("Salva nel Cloud"):
    if causale:
        # Scrive fisicamente nel database di Google
        doc_ref = db.collection("transazioni").document()
        doc_ref.set({
            "importo": importo,
            "causale": causale,
            "utente": "admin"
        })
        st.success("Transazione salvata in modo permanente nel Cloud!")
    else:
        st.warning("Inserisci una causale.")