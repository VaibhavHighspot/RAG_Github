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
import requests
import json

# Load environment variables
load_dotenv()

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
            "user-agent": "MyApp/1.0 (https://example.com)"
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

# Streamlit session setup
if "id" not in st.session_state:
    st.session_state.id = uuid.uuid4()
    st.session_state.file_cache = {}

session_id = st.session_state.id

def reset_chat():
    """Resets the chat history and session context."""
    st.session_state.messages = []
    st.session_state.context = None
    gc.collect()

def process_with_gitingest(github_url):
    """
    Processes a GitHub repository using the gitingest library.

    Args:
        github_url (str): The GitHub repository URL.

    Returns:
        tuple: Summary, tree, and content of the repository.
    """
    summary, tree, content = ingest(github_url)
    return summary, tree, content

# Sidebar for GitHub repository input
with st.sidebar:
    st.header("Add your GitHub repository!")
    
    github_url = st.text_input("Enter GitHub repository URL", placeholder="GitHub URL")
    load_repo = st.button("Load Repository")

    if github_url and load_repo:
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                st.write("Processing your repository...")
                repo_name = github_url.split('/')[-1]
                file_key = f"{session_id}-{repo_name}"
                
                if file_key not in st.session_state.get('file_cache', {}):
                    # Repository processing logic
                    summary, tree, content = process_with_gitingest(github_url)
                    st.session_state.file_cache[file_key] = {"summary": summary, "tree": tree, "content": content}
                else:
                    st.write("Repository already loaded.")

                st.success("Ready to Chat!")
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.stop()     

# Main chat interface
col1, col2 = st.columns([6, 1])

with col1:
    st.header("Chat with GitHub using RAG </>")

with col2:
    st.button("Clear ↺", on_click=reset_chat)

# Initialize chat history
if "messages" not in st.session_state:
    reset_chat()

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input and assistant response
if prompt := st.chat_input("What's up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            full_response = interact_with_llm(prompt)
            message_placeholder.markdown(full_response)
        except Exception as e:
            full_response = "Sorry, I encountered an error while processing your request."
            st.error(f"Error: {e}")
            message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})

