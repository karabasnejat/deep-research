import streamlit as st

st.set_page_config(page_title="Deep Research Agent", layout="wide")

st.title("Deep Research Agent")

# Sidebar: Settings/API Keys
with st.sidebar:
    st.header("Settings")
    serpapi_key = st.text_input("SerpAPI Key", type="password")
    openai_key = st.text_input("OpenAI API Key", type="password")
    arxiv_key = st.text_input("ArXiv API Key", type="password")
    pubmed_key = st.text_input("PubMed API Key", type="password")
    st.markdown("---")
    st.info("Enter your API keys to enable research features.")

# Main input area
st.subheader("Enter your research topic")
topic = st.text_input("Topic or question", "")
start_btn = st.button("Start Research")

st.markdown("---")

# Layout: 3 columns for main panels
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    st.subheader("Chat Panel")
    st.info("Chat history will appear here.")

with col2:
    st.subheader("Report Panel")
    st.info("Research report will be shown here.")

with col3:
    st.subheader("Chain-of-Thought")
    st.info("Agent reasoning steps will be visualized here.")
    st.markdown("---")
    st.subheader("Memory Panel")
    st.info("Short/Long-term memory will be listed here.") 