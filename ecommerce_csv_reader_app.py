import streamlit as st
import pandas as pd
import os
import gdown
#from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
#from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

st.set_page_config(page_title="CSV FAQ Agent", page_icon="🤖")
st.title("🤖 CSV FAQ Agent")
st.caption("Ask questions across SaaS Docs, Credit Card Terms, Hospital Policy, and Ecommerce FAQs.")

# ==========================================
#  FILE DOWNLOADER (runs once, cached)
# ==========================================
files_to_download = {
    "saas_docs.csv":         "https://drive.google.com/file/d/1RElOhN7bYsDAJUNQhYyqM7IzX-Xo6myq/view?usp=sharing",
    "credit_card_terms.csv": "https://drive.google.com/file/d/1_giivc_B0urOKpct0XY2yVZuxW3Eenuf/view?usp=sharing",
    "hospital_policy.csv":   "https://drive.google.com/file/d/1pL7OnDhnmz9pteIpBJ12gu2_ixrc2hPm/view?usp=sharing",
    "ecommerce_faqs.csv":    "https://drive.google.com/file/d/1O4fTjsLFbz55oOiwJUwLwZryO5OSSF6p/view?usp=sharing"
}

@st.cache_resource(show_spinner="Downloading data files...")
def download_files():
    for filename, url in files_to_download.items():
        if not os.path.exists(filename):
            gdown.download(url, filename, quiet=True)
    return True

download_files()

# ==========================================
#  SIDEBAR: API KEY INPUT
# ==========================================
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter your AI API Key", type="password")
    st.caption("Get a key at https://platform.openai.com/api-keys")

if not api_key:
    st.info("Please enter your AI API key in the sidebar to get started.")
    st.stop()

# ==========================================
#  BUILD THE AGENT (cached so it's not rebuilt on every message)
# ==========================================
@st.cache_resource(show_spinner="Setting up the agent...")
def build_agent(_api_key):
    dataframes = [pd.read_csv(filename) for filename in files_to_download.keys()]

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0, api_key=_api_key)

    agent = create_pandas_dataframe_agent(
        llm,
        dataframes,
        verbose=True,
        agent_type="zero-shot-react-description",
        allow_dangerous_code=True
    )
    return agent

try:
    agent = build_agent(api_key)
except Exception as e:
    st.error(f"Error initializing agent: {e}")
    st.stop()

system_prompt = """
You are a smart data assistant capable of reading multiple CSV files.
- You have access to 4 different datasets: SaaS Docs, Credit Card Terms, Hospital Policy, and Ecommerce FAQs.
- When asked a question, determine which DataFrame is most relevant.
- Do NOT answer from general knowledge.
- Answer in plain English.
"""

# ==========================================
#  CHAT INTERFACE
# ==========================================

# Keep chat history across reruns
if "messages" not in st.session_state:
    st.session_state.messages = []

# Replay previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# New user input
user_input = st.chat_input("Ask a question, e.g. 'What is the visiting hour in the hospital?'")

if user_input:
    # Show and store the user's message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get and show the AI's response
    with st.chat_message("assistant"):
        with st.spinner("AI is thinking..."):
            try:
                final_query = system_prompt + "\n\nQuestion: " + user_input
                response = agent.invoke(final_query)
                answer = response["output"]
            except Exception as e:
                answer = f"An error occurred: {e}"
            st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
