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
        prompt (str): The prompt to send to the LLM.

    Returns:
        str: The response from the LLM.
    """
    llm_response = None
    try:
        url = "https://ai-services.k8s.latest0-su0.hspt.io/llm/general"
        payload = {
            "prompt_key": "chat_bot",
            "messages": [{"role": "user", "content": prompt}]
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        response_object = response.json()
        llm_response = response_object.get("choices", [{}])[0].get("text", "No response")
    except Exception as e:
        llm_response = f"Unable to generate user insights summary: {str(e)}"
    return llm_response

load_dotenv()

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


with st.sidebar:
    st.header(f"Add your GitHub repository!")
    
    github_url = st.text_input("Enter GitHub repository URL", placeholder="GitHub URL")
    load_repo = st.button("Load Repository")

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
