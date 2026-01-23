import streamlit as st
import os
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai import OpenAI # We import the class explicitly
import qdrant_client

st.set_page_config(page_title="Financial Analyst AI", layout="centered")
st.title("📊 AI Financial Analyst")

# Sidebar
with st.sidebar:
    st.header("🔐 API Keys")
    openai_key = st.text_input("OpenAI API Key (Starts with sk-)", type="password")
    qdrant_url = st.text_input("Qdrant Cluster URL", type="default")
    qdrant_key = st.text_input("Qdrant API Key", type="password")
    
    # Add a reset button
    if st.button("Reset / Clear Cache"):
        st.cache_resource.clear()
        st.rerun()

@st.cache_resource
def load_rag_engine(api_key, q_url, q_key):
    # FORCE the LLM to use the provided key immediately
    # This prevents it from using a 'stuck' environment variable
    llm = OpenAI(model="gpt-4o-mini", api_key=api_key)
    Settings.llm = llm
    
    # Load Embeddings
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    
    # Connect to Qdrant
    client = qdrant_client.QdrantClient(url=q_url, api_key=q_key)
    vector_store = QdrantVectorStore(client=client, collection_name="financial_filings")
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    return VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context).as_query_engine(similarity_top_k=5)

if openai_key and qdrant_url and qdrant_key:
    try:
        # Pass keys directly to the function
        engine = load_rag_engine(openai_key, qdrant_url, qdrant_key)
        
        query = st.text_input("Ask a question:", placeholder="Compare Microsoft and Google cloud growth")
        
        if st.button("Analyze Report"):
            with st.spinner("🤖 Consulting the 10-K filings..."):
                response = engine.query(query)
                st.success("Analysis Complete!")
                st.markdown(f"### Answer:\n{response}")
                
    except Exception as e:
        st.error(f"Error: {e}")
        st.info("Try clicking the 'Reset / Clear Cache' button in the sidebar.")
else:
    st.warning("👈 Enter keys to start.")