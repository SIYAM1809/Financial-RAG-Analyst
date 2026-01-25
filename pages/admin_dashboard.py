import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Admin Observability", layout="wide")

st.title("🕵️‍♂️ RAG Observability Dashboard")
st.markdown("### Monitor AI Performance & Hallucinations")

# --- AUTHENTICATION (SECURE) ---
# 1. Check if the password is set in Secrets
if "ADMIN_PASSWORD" not in st.secrets:
    st.error("🚨 Admin password not set in Streamlit Secrets.")
    st.stop()

correct_password = st.secrets["ADMIN_PASSWORD"]

# 2. Input Field
user_password = st.sidebar.text_input("Admin Password", type="password")

# 3. Logic: Empty vs. Wrong
if not user_password:
    st.info("🔒 Please enter the admin password in the sidebar to access.")
    st.stop()
elif user_password != correct_password:
    st.error("❌ Incorrect Password.")
    st.stop()
else:
    st.sidebar.success("Access Granted ✅")

# --- DASHBOARD LOGIC (Only runs if password is correct) ---

# Load Data
if not os.path.exists("rag_logs.csv"):
    st.warning("No logs found yet. Go ask some questions in the main app to generate data!")
    st.stop()

try:
    df = pd.read_csv("rag_logs.csv")
except Exception as e:
    st.error(f"Error reading log file: {e}")
    st.stop()

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
    # Check if there is actual data to plot to avoid Plotly errors
    if df['Feedback'].notna().any():
        fig = px.pie(df, names='Feedback', title='User Satisfaction Rate', hole=0.4)
        st.plotly_chart(fig)
    else:
        st.info("Waiting for first feedback rating...")

# --- RAW LOGS ---
st.subheader("📝 Recent Interaction Logs")
st.dataframe(df.sort_index(ascending=False), use_container_width=True)