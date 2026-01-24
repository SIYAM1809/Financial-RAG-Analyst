import streamlit as st
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq # <--- New Import
import qdrant_client

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Financial RAG Analyst", page_icon="📈", layout="wide")

st.markdown(
    """
    <style>
        .stApp { background-color: #0E1117; color: #FAFAFA; font-family: 'Inter', sans-serif; }
        h1 { background: -webkit-linear-gradient(45deg, #FF5722, #FFC107); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .stTextInput > div > div > input { background-color: #374151; color: white; border-radius: 8px; }
        .stButton > button { background: linear-gradient(45deg, #FF5722, #FFC107); color: white; border: none; padding: 12px 24px; border-radius: 8px; }
        [data-testid="stSidebar"] { display: none; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- 2. LOAD ENGINE (Using Free Groq) ---
@st.cache_resource(show_spinner=False)
def load_rag_engine():
    # 1. Fetch keys securely
    if "GROQ_API_KEY" not in st.secrets:
        st.error("🚨 Owner has not set up Groq API keys.")
        st.stop()
        
    groq_key = st.secrets["GROQ_API_KEY"]
    q_url = st.secrets["QDRANT_URL"]
    q_key = st.secrets["QDRANT_API_KEY"]
    
    # 2. Configure Groq (Llama 3) - COMPLETELY FREE
    llm = Groq(model="llama3-8b-8192", api_key=groq_key)
    Settings.llm = llm
    
    # 3. Embeddings (Still using free HuggingFace model)
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    
    # 4. Connect to Vector DB
    client = qdrant_client.QdrantClient(url=q_url, api_key=q_key)
    vector_store = QdrantVectorStore(client=client, collection_name="financial_filings")
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    return VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context).as_query_engine(similarity_top_k=5)

# --- 3. MAIN INTERFACE ---
st.title("⚡ AI Financial Analyst (Free Ed.)")
st.markdown("### Powered by Llama 3 & Groq (Zero Cost)")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Compare Microsoft and Google cloud growth..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        engine = load_rag_engine()
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking at lightspeed..."):
                response = engine.query(prompt)
                st.markdown(response)
                
        st.session_state.messages.append({"role": "assistant", "content": str(response)})

    except Exception as e:
        st.error(f"An error occurred: {e}")