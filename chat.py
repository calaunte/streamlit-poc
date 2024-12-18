import streamlit as st
import requests
import json

# Define model options with their corresponding URLs
MODEL_OPTIONS = {
    "meta/llama-2-7b-chat": "http://0.0.0.0:8000/v1/chat/completions",
    "nv-mistralai/mistral-nemo-minitron-8b-8k-instruct": "http://0.0.0.0:8080/v1/chat/completions",
}

def get_last_exchange(messages):
    """
    Get only the last user message for the API call.
    """
    if not messages:
        return []
        
    # Get only the last user message
    for msg in reversed(messages):
        if msg["role"] == "user":
            return [msg]
            
    return []

def make_api_call(messages, model, api_endpoint):
    """
    Make a chat completion API call
    """
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # Get only the last user message
    formatted_messages = get_last_exchange(messages)
    
    payload = {
        "model": model,
        "messages": formatted_messages,
        "top_p": 1,
        "n": 1,
        "max_tokens": 600
    }

    try:
        response = requests.post(api_endpoint, headers=headers, json=payload)
            
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error making request: {e}")
        return None

# Sidebar for model selection
with st.sidebar:
    selected_model = st.selectbox(
        "Select Model",
        options=list(MODEL_OPTIONS.keys()),
        key="model_selector"
    )
    
    api_endpoint = MODEL_OPTIONS[selected_model]

# Main chat interface
st.title("💬 Chatbot")
st.caption("Streamlit chatbot powered by Nvidia NIM")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display chat history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Chat input and response
if prompt := st.chat_input():
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Make API call
    response = make_api_call(
        messages=st.session_state.messages,
        model=selected_model,
        api_endpoint=api_endpoint
    )

    # Process response
    if response and 'choices' in response:
        msg = response['choices'][0]['message']['content']
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.chat_message("assistant").write(msg)
    else:
        st.error("Failed to get response from the API")