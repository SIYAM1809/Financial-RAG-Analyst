import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Admin Observability", layout="wide")

st.title("🕵️‍♂️ RAG Observability Dashboard")
st.markdown("### Monitor AI Performance & Hallucinations")

# Passphrase protection
password = st.sidebar.text_input("Admin Password", type="password")
if password != "siyam44":
    st.warning("Please enter admin password.")
    st.stop()

# Load Data
if not os.path.exists("rag_logs.csv"):
    st.info("No logs found yet. Go ask some questions in the main app!")
    st.stop()

df = pd.read_csv("rag_logs.csv")

# --- KPI METRICS ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Queries", len(df))
with col2:
    # Count "Positive" feedback
    if 'Feedback' in df.columns:
        positive_count = df[df['Feedback'] == 'Positive'].shape[0]
    else:
        positive_count = 0
    st.metric("👍 Helpful Answers", positive_count)
with col3:
    # Count "Negative" feedback
    if 'Feedback' in df.columns:
        negative_count = df[df['Feedback'] == 'Negative'].shape[0]
    else:
        negative_count = 0
    st.metric("🚩 Hallucinations Flagged", negative_count)

st.markdown("---")

# --- VISUALIZATION ---
st.subheader("📊 Feedback Distribution")
if not df.empty and 'Feedback' in df.columns:
    fig = px.pie(df, names='Feedback', title='User Satisfaction Rate', hole=0.4)
    st.plotly_chart(fig)

# --- RAW LOGS ---
st.subheader("📝 Recent Interaction Logs")
st.dataframe(df.sort_index(ascending=False), use_container_width=True)
