import streamlit as st
import os
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import qdrant_client

# 1. Basic Page Config
st.set_page_config(page_title="Financial Analyst AI", layout="centered")
st.title("📊 AI Financial Analyst")
st.write("Ask questions about Apple, Microsoft, and Google 2024 10-K filings.")

# 2. Sidebar for Secrets (Best practice for public apps)
with st.sidebar:
    st.header("🔐 API Keys")
    st.info("Enter your keys to activate the AI.")
    openai_key = st.text_input("OpenAI API Key", type="password")
    qdrant_url = st.text_input("Qdrant Cluster URL", type="default")
    qdrant_key = st.text_input("Qdrant API Key", type="password")

# 3. The "Load" Function (Cached for speed)
@st.cache_resource
def load_rag_engine(api_key, q_url, q_key):
    # Set OpenAI Key
    os.environ["OPENAI_API_KEY"] = api_key
    
    # Load the "Brain" from the Cloud
    client = qdrant_client.QdrantClient(url=q_url, api_key=q_key)
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    
    vector_store = QdrantVectorStore(client=client, collection_name="financial_filings")
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)
    
    return index.as_query_engine(similarity_top_k=5)

# 4. Main Chat Logic
if openai_key and qdrant_url and qdrant_key:
    try:
        # Load the engine
        engine = load_rag_engine(openai_key, qdrant_url, qdrant_key)
        
        # User Input
        query = st.text_input("Ask a question:", placeholder="e.g., Compare Microsoft and Google cloud growth")
        
        if st.button("Analyze Report"):
            with st.spinner("🤖 Consulting the 10-K filings..."):
                response = engine.query(query)
                st.success("Analysis Complete!")
                st.markdown(f"### Answer:\n{response}")
                
    except Exception as e:
        st.error(f"Error connecting: {e}")
else:
    st.warning("👈 Please enter your API keys in the sidebar to start.")
