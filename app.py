import streamlit as st
import os
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai import OpenAI
import qdrant_client

# --- 1. PAGE CONFIG & CUSTOM CSS ---
st.set_page_config(
    page_title="Financial RAG Analyst",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for a premium, dark-themed look
st.markdown(
    """
    <style>
        /* Main Background & Font */
        .stApp {
            background-color: #0E1117;
            color: #FAFAFA;
            font-family: 'Inter', sans-serif;
        }
        
        /* Headings */
        h1 {
            font-weight: 700;
            background: -webkit-linear-gradient(45deg, #4F46E5, #06B6D4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            padding-bottom: 1rem;
        }
        h2, h3 {
            font-weight: 600;
            color: #E5E7EB;
        }
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #1F2937;
            border-right: 1px solid #374151;
        }
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
            color: #F9FAFB;
        }
        
        /* Input Fields */
        .stTextInput > div > div > input {
            background-color: #374151;
            color: #F9FAFB;
            border: 1px solid #4B5563;
            border-radius: 8px;
            padding: 10px;
        }
        .stTextInput > div > div > input:focus {
            border-color: #4F46E5;
            box-shadow: 0 0 0 1px #4F46E5;
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(45deg, #4F46E5, #06B6D4);
            color: white;
            font-weight: 600;
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            opacity: 0.9;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
        }
        
        /* Success/Info Boxes */
        .stSuccess, .stInfo, .stWarning {
            background-color: #1F2937 !important;
            color: #F9FAFB !important;
            border: 1px solid #374151;
            border-radius: 8px;
        }
        
        /* Hide Streamlit Elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Answer Container */
        .answer-container {
            background-color: #1F2937;
            padding: 25px;
            border-radius: 12px;
            border: 1px solid #374151;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- 2. SIDEBAR FOR SECRETS ---
with st.sidebar:
    st.title("🔐 Credentials")
    st.markdown("Please enter your API keys to unlock the financial analysis engine.")
    
    with st.expander("API Key Inputs", expanded=True):
        openai_key = st.text_input("OpenAI API Key (Starts with sk-)", type="password", help="Get this from platform.openai.com")
        qdrant_url = st.text_input("Qdrant Cluster URL", type="default", help="Your Qdrant Cloud cluster URL")
        qdrant_key = st.text_input("Qdrant API Key", type="password", help="Your Qdrant Cloud API key")
    
    st.markdown("---")
    st.caption("Troubleshooting")
    if st.button("🔄 Reset / Clear Cache", help="Click this if the app seems stuck or isn't using new keys."):
        st.cache_resource.clear()
        st.rerun()

# --- 3. THE "LOAD" FUNCTION (Cached) ---
@st.cache_resource
def load_rag_engine(api_key, q_url, q_key):
    # FORCE the LLM to use the provided key immediately
    llm = OpenAI(model="gpt-4o-mini", api_key=api_key)
    Settings.llm = llm
    
    # Load Embeddings
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    
    # Connect to Qdrant
    client = qdrant_client.QdrantClient(url=q_url, api_key=q_key)
    vector_store = QdrantVectorStore(client=client, collection_name="financial_filings")
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    return VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context).as_query_engine(similarity_top_k=5)

# --- 4. MAIN PAGE LAYOUT ---
# Header
col1, col2 = st.columns([1, 5])
with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/2709/2709753.png", width=100) # Placeholder Icon
with col2:
    st.title("AI Financial Analyst")
    st.markdown("### Intelligent Insights from SEC 10-K Filings")
    st.markdown("Ask complex questions about Apple, Microsoft, and Google's 2024 financial reports. The AI will verify facts directly from the source documents.")

st.markdown("---")

# Main Logic
if openai_key and qdrant_url and qdrant_key:
    try:
        engine = load_rag_engine(openai_key, qdrant_url, qdrant_key)
        
        # Input Area with columns
        input_col, btn_col = st.columns([4, 1])
        with input_col:
            query = st.text_input("Enter your question:", placeholder="e.g., 'Compare the cloud revenue growth of Microsoft Azure vs. Google Cloud in 2024.'", label_visibility="collapsed")
        with btn_col:
            # Add some top padding to align with text input
            st.markdown("<div style='padding-top: 0px;'></div>", unsafe_allow_html=True)
            analyze_button = st.button("🔍 Analyze Report", use_container_width=True)
        
        if analyze_button:
            if not query:
                st.warning("Please enter a question first.")
            else:
                with st.spinner("🤖 Consulting the 10-K filings... This may take a moment."):
                    response = engine.query(query)
                
                st.markdown("<br>", unsafe_allow_html=True) # Spacer
                
                # Premium Answer Display
                with st.container():
                    st.markdown("""<div class="answer-container">""", unsafe_allow_html=True)
                    st.markdown("## 💡 Analysis Result")
                    st.success("Answer generated successfully from document retrieval.")
                    st.markdown(f"{response}", unsafe_allow_html=True)
                    st.markdown("""</div>""", unsafe_allow_html=True)
                
    except Exception as e:
        st.error(f"**Connection Error:** {e}")
        st.info("👉 Try clicking the 'Reset / Clear Cache' button in the sidebar.")
else:
    # Empty State Hero
    st.markdown(
        """
        <div style="text-align: center; padding: 50px 20px; color: #9CA3AF;">
            <h1>Ready to get started?</h1>
            <p style="font-size: 1.2rem;">👈 Enter your API keys in the sidebar to unlock the power of AI financial analysis.</p>
            <img src="https://cdn-icons-png.flaticon.com/512/1162/1162998.png" width="150" style="opacity: 0.5; margin-top: 20px;">
        </div>
        """,
        unsafe_allow_html=True
    )