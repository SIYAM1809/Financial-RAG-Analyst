import streamlit as st
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
import qdrant_client
import logger  # <--- IMPORT YOUR NEW LOGGER

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Financial RAG Analyst", page_icon="📈", layout="wide")

st.markdown(
    """
    <style>
        .stApp { background-color: #0E1117; color: #FAFAFA; font-family: 'Inter', sans-serif; }
        h1 { background: -webkit-linear-gradient(45deg, #FF5722, #FFC107); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .stTextInput > div > div > input { background-color: #374151; color: white; border-radius: 8px; }
        .stButton > button { background: linear-gradient(45deg, #FF5722, #FFC107); color: white; border: none; padding: 12px 24px; border-radius: 8px; }
        /* I removed the 'Hide Sidebar' CSS so you can access the Admin Dashboard */
    </style>
    """,
    unsafe_allow_html=True,
)

# --- 2. LOAD ENGINE (Using Free Groq Llama 3.1) ---
@st.cache_resource(show_spinner=False)
def load_rag_engine():
    # 1. Fetch keys securely
    if "GROQ_API_KEY" not in st.secrets:
        st.error("🚨 Owner has not set up Groq API keys.")
        st.stop()
        
    groq_key = st.secrets["GROQ_API_KEY"]
    q_url = st.secrets["QDRANT_URL"]
    q_key = st.secrets["QDRANT_API_KEY"]
    
    # 2. Configure Groq (UPDATED to Llama 3.1)
    llm = Groq(model="llama-3.1-8b-instant", api_key=groq_key) 
    Settings.llm = llm
    
    # 3. Embeddings (Still using free HuggingFace model)
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    
    # 4. Connect to Vector DB
    client = qdrant_client.QdrantClient(url=q_url, api_key=q_key)
    vector_store = QdrantVectorStore(client=client, collection_name="financial_filings")
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    return VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context).as_query_engine(similarity_top_k=5)

# --- 3. MAIN INTERFACE ---
st.title("⚡ AI Financial Analyst (Pro)")
st.markdown("### Powered by Llama 3.1 & Groq")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- THE NEW OBSERVABILITY LOOP ---
if prompt := st.chat_input("Compare Microsoft and Google cloud growth..."):
    # 1. Show User Message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        engine = load_rag_engine()
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking at lightspeed..."):
                # 2. Generate Answer
                response_obj = engine.query(prompt)
                response_text = str(response_obj)
                st.markdown(response_text)
                
                # 3. Log the interaction immediately (Feedback is 'Pending' for now)
                logger.log_interaction(prompt, response_text, "Pending")
                
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        st.rerun() # Force refresh to show feedback buttons below

    except Exception as e:
        st.error(f"An error occurred: {e}")

# --- FEEDBACK MECHANISM (The "1%" Feature) ---
# If the last message was from the AI, show feedback buttons
if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
    st.write("---")
    
    # 1. CHANGED: Ratios [2, 2, 6] give the buttons 2x more width than before
    col1, col2, col3 = st.columns([3, 3, 8])
    
    with col1:
        # 2. CHANGED: 'use_container_width=True' forces the button to stretch
        if st.button("👍 Good Answer", use_container_width=True):
            logger.log_interaction(
                st.session_state.messages[-2]["content"], # The Question
                st.session_state.messages[-1]["content"], # The Answer
                "Positive"
            )
            st.toast("Thanks for the feedback! (Logged to System)")
            
    with col2:
        # 2. CHANGED: 'use_container_width=True' prevents the text from wrapping
        if st.button("👎 Bad/Hallucinated", use_container_width=True):
            logger.log_interaction(
                st.session_state.messages[-2]["content"], 
                st.session_state.messages[-1]["content"], 
                "Negative"
            )
            st.toast("Flagged for review. We will improve this.")