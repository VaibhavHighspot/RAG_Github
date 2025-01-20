import os
import gc
import tempfile
import uuid
import pandas as pd
from gitingest import ingest
from llama_index.core import Settings
from llama_index.core import PromptTemplate
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.node_parser import MarkdownNodeParser
import streamlit as st
from dotenv import load_dotenv
import requests  # Add this if it's not already imported
import json  # Add this if it's not already imported

# Function to interact with the company's LLM API


def interact_with_llm(prompt):
    """
    Sends a prompt to the company's LLM API and returns the response.

    Args:
        prompt (str): The user input or data to send to the LLM.

    Returns:
        str: The response from the LLM API.
    """
    llm_response = None
    try:
        url = "https://ai-services.k8s.latest0-su0.hspt.io/llm/general"
        payload = {
            "prompt_key": "chat_bot",
            "messages": prompt
        }
        headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "hs-csrf": "Mwg6RSnCreIG3a1ac4KWACBo3vstVs0GHmkHeby5cxuC",
            "hs-user-id": "66f12c2ba53d627ee971643f",
            "origin": "http://localhost:3000",
            "priority": "u=1, i",
            "referer": "http://localhost:3000/items/67160fbca53d6268ea23535f?lfrm=shp.5&learning_path_version=current",
            "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        }

        # Send a POST request to the API
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()  # Raise exception for HTTP errors

        # Parse the API response
        response_object = response.json()
        llm_response = response_object.get("choices", [{}])[0].get("text", "No response available")
    except Exception as e:
        llm_response = f"Unable to generate user insights summary: {str(e)}"

    return llm_response


load_dotenv()

import streamlit as st

# Set up the page layout
st.set_page_config(page_title="Highspot Chatbot", layout="wide")

# Header Section with Highspot Branding
st.markdown("""
    <style>
    .header {
        text-align: center;
        font-size: 2.5em;
        font-weight: bold;
        color: #0074d9; /* Highspot blue color */
        margin-top: 20px;
    }
    .description {
        text-align: center;
        font-size: 1.2em;
        margin-top: 10px;
    }
    .highspot-card {
        background-color: #f7f9fa;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
        margin: 20px auto;
        width: 80%;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Company Name & Description
st.markdown('<div class="header">Highspot Gitbot</div>', unsafe_allow_html=True)
st.markdown('<div class="description">Welcome to the Highspot-powered assistant! Get insights from your GitHub repositories and chat with our AI.</div>', unsafe_allow_html=True)

# Sidebar for GitHub Repository Input
with st.sidebar:
    st.header("Add your GitHub repository!")
    github_url = st.text_input("Enter GitHub repository URL", placeholder="GitHub URL", key="github_url_input")  # Add unique key
    load_repo = st.button("Load Repository", key="load_repo_button")  # Add unique key for the button

    if github_url and load_repo:
        st.success("Repository Loaded Successfully!")

# Chat Interface (Message Input and Display)
st.markdown("""
    <div class="highspot-card">
    <h3>Start a Conversation:</h3>
    <p>Ask questions about your repository or just chat!</p>
    </div>
""", unsafe_allow_html=True)

# Placeholder for user interaction (e.g., a simple chat input box)
prompt = st.text_input("Type your question here:", placeholder="Ask about the repository...", key="chat_input")  # Add unique key

if prompt:
    st.markdown(f"**You asked**: {prompt}")
    # Example response, in a real app this will be replaced by LLM response
    st.markdown(f"**Assistant**: Here’s the response to your question about `{prompt}`.")

# Add all your imports here (as shown earlier)

# Add the interact_with_llm function here (as shown above)

load_dotenv()

if "id" not in st.session_state:
    st.session_state.id = uuid.uuid4()
    st.session_state.file_cache = {}

session_id = st.session_state.id
client = None

def reset_chat():
    st.session_state.messages = []
    st.session_state.context = None
    gc.collect()

def process_with_gitingets(github_url):
    # or from URL
    summary, tree, content = ingest(github_url)
    return summary, tree, content


# with st.sidebar:
#     st.header(f"Add your GitHub repository!")
    
#     github_url = st.text_input("Enter GitHub repository URL", placeholder="GitHub URL")
#     load_repo = st.button("Load Repository")

    if github_url and load_repo:
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                st.write("Processing your repository...")
                repo_name = github_url.split('/')[-1]
                file_key = f"{session_id}-{repo_name}"
                
                if file_key not in st.session_state.get('file_cache', {}):
                    # Your repository processing logic here
                    st.session_state.file_cache[file_key] = True  # Placeholder for query engine
                else:
                    st.write("Repository already loaded.")

                st.success("Ready to Chat!")
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.stop()     

col1, col2 = st.columns([6, 1])

with col1:
    st.header(f"Chat with GitHub using RAG </>")

with col2:
    st.button("Clear ↺", on_click=reset_chat)

# Initialize chat history
if "messages" not in st.session_state:
    reset_chat()

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What's up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            # Use the interact_with_llm function to process the prompt
            full_response = interact_with_llm(prompt)
            message_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"An error occurred while processing your query: {str(e)}")
            full_response = "Sorry, I encountered an error while processing your request."
            message_placeholder.markdown(full_response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
