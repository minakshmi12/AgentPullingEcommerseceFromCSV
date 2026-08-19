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
    # Load DataFrames with proper error handling
    dataframes = []
    df_names = []
    for filename in files_to_download.keys():
        try:
            df = pd.read_csv(filename)
            dataframes.append(df)
            # Extract dataset name from filename
            name = filename.replace(".csv", "").replace("_", " ").title()
            df_names.append(name)
        except FileNotFoundError:
            st.error(f"File not found: {filename}")
            st.stop()

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0, api_key=_api_key)

    # Create agent with proper system message
    agent = create_pandas_dataframe_agent(
        llm,
        dataframes,
        verbose=True,
        agent_type="openai-functions",
        allow_dangerous_code=True,
        prefix="""You are a helpful data assistant with access to multiple CSV datasets: {}

Instructions:
- Always search the relevant dataset to answer questions
- Cite the specific data you find in the CSV
- Do NOT answer from general knowledge - only use the provided CSV data
- If data is not found in the CSVs, say "I could not find this information in the available data"
- Format your answer in clear, customer-friendly English""".format(", ".join(df_names))
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
                # Pass the user input directly to the agent
                response = agent.invoke({"input": user_input})
                answer = response["output"]
            except Exception as e:
                answer = f"An error occurred: {e}"
            st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
