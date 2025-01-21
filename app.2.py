import os
import gc
import uuid
import tempfile
from sentence_transformers import SentenceTransformer, util
from langchain_groq import ChatGroq
from gitingest import ingest
import streamlit as st
# Initialize ChatGroq with settings
def initialize_llm():
    return ChatGroq(
         temperature=0.1,
         groq_api_key='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',
         model_name="llama-3.1-70b-versatile"
    )
# Embed repository content
def embed_content(content, model_name="all-MiniLM-L6-v2"):
    embedder = SentenceTransformer(model_name)
    sentences = content.split("\n")  # Split content into lines or sentences
    embeddings = embedder.encode(sentences, convert_to_tensor=True)
    return sentences, embeddings
# Find top-k similar chunks
def find_top_k_similar_chunks(query, embeddings, sentences, k=2):
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    query_embedding = embedder.encode(query, convert_to_tensor=True)
    similarities = util.pytorch_cos_sim(query_embedding, embeddings)[0]
    top_k_indices = similarities.topk(k).indices
    return [sentences[idx] for idx in top_k_indices]
# Ingest GitHub content
def ingest_github_repo(github_url):
    summary, tree, content = ingest(github_url)
    return content  # Only return the content for embeddings
# Process the user query
def process_query(query, github_url, llm, k=2):
    # Ingest GitHub repo content
    content = ingest_github_repo(github_url)
    sentences, embeddings = embed_content(content)
    # Find top-k similar chunks
    top_chunks = find_top_k_similar_chunks(query, embeddings, sentences, k)
    combined_context = "\n".join(top_chunks)
    # Create prompt and get response from ChatGroq
    prompt = (
        f"Take the github repository as an input, understand all terms from the code."
        f"now answer only to the question asked. generate the required explanation :\n\n{combined_context}\n\nQuery: {query}"
    )
    response = llm.invoke(prompt)
    return response
# Streamlit app
st.title("ChatGroq: Interact with GitHub Repositories")
st.sidebar.header("GitHub Input")
github_url = st.sidebar.text_input("Enter GitHub Repository URL", "")
user_query = st.text_input("Ask a question about the repository", "")
submit = st.button("Submit")
if submit:
    if not github_url or not user_query:
        st.error("Please enter a GitHub URL and a query.")
    else:
        with st.spinner("Processing..."):
            try:
                # Initialize ChatGroq
                llm = initialize_llm()
                # Process the query
                answer = process_query(user_query, github_url, llm, k=3)
                # Display the response
                st.success("Answer:")
                st.write(answer)
            except Exception as e:
                st.error(f"An error occurred: {e}")

# import os
# import gc
# import uuid
# import tempfile
# from sentence_transformers import SentenceTransformer, util
# from langchain_groq import ChatGroq
# from gitingest import ingest
# import streamlit as st

# # Initialize ChatGroq with settings
# def initialize_llm():
#     return ChatGroq(
#         temperature=0.1,
#         groq_api_key='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',
#         model_name="llama-3.1-70b-versatile"
#     )

# # Embed repository content
# def embed_content(content, model_name="all-MiniLM-L6-v2"):
#     embedder = SentenceTransformer(model_name)
#     sentences = content.split("\n")  # Split content into lines or sentences
#     embeddings = embedder.encode(sentences, convert_to_tensor=True)
#     return sentences, embeddings

# # Find top-k similar chunks
# def find_top_k_similar_chunks(query, embeddings, sentences, k=2):
#     embedder = SentenceTransformer("all-MiniLM-L6-v2")
#     query_embedding = embedder.encode(query, convert_to_tensor=True)
#     similarities = util.pytorch_cos_sim(query_embedding, embeddings)[0]
#     top_k_indices = similarities.topk(k).indices
#     return [sentences[idx] for idx in top_k_indices]

# # Ingest GitHub content
# def ingest_github_repo(github_url):
#     summary, tree, content = ingest(github_url)
#     return content  # Only return the content for embeddings

# # Process the user query
# def process_query(query, github_url, llm, k=2):
#     # Ingest GitHub repo content
#     content = ingest_github_repo(github_url)
#     sentences, embeddings = embed_content(content)
#     # Find top-k similar chunks
#     top_chunks = find_top_k_similar_chunks(query, embeddings, sentences, k)
#     combined_context = "\n".join(top_chunks)
#     # Create refined prompt
#     prompt = (
#         f"You are a helpful Q&A assistant. Using the following context from the GitHub repository, "
#         f"answer the question concisely and without including any extra information or code:\n\n{combined_context}\n\nQuery: {query}\n\nAnswer:"
#     )
#     # Get the response from ChatGroq
#     response = llm.invoke(prompt, max_tokens=150)  # Limit the response length to 150 tokens
#     # Post-process the response if necessary
#     answer = response.split("Answer:")[-1].strip()  # Extract only the answer part
#     return answer

# # Streamlit app
# st.title("ChatGroq: Interact with GitHub Repositories")
# st.sidebar.header("GitHub Input")
# github_url = st.sidebar.text_input("Enter GitHub Repository URL", "")
# user_query = st.text_input("Ask a question about the repository", "")
# submit = st.button("Submit")

# if submit:
#     if not github_url or not user_query:
#         st.error("Please enter a GitHub URL and a query.")
#     else:
#         with st.spinner("Processing..."):
#             try:
#                 # Initialize ChatGroq
#                 llm = initialize_llm()
#                 # Process the query
#                 answer = process_query(user_query, github_url, llm, k=3)
#                 # Display the response
#                 st.success("Answer:")
#                 st.write(answer)
#             except Exception as e:
#                 st.error(f"An error occurred: {e}")
