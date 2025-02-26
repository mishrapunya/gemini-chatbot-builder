import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Page configuration
st.set_page_config(
    page_title="Gemini Chatbot Builder",
    page_icon="🤖",
    layout="wide"
)

# Load environment variables
load_dotenv()

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "bot_name" not in st.session_state:
    st.session_state.bot_name = "Gemini Assistant"

if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = "You are a helpful assistant named Gemini Assistant. You're friendly, concise, and informative. When answering questions, provide accurate information and be honest when you don't know something."

if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7

if "model" not in st.session_state:
    st.session_state.model = "gemini-1.5-pro"

# Title and description
st.title("🤖 Gemini Chatbot Builder")
st.markdown("Configure and test your Gemini-powered chatbot with this builder interface.")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    
    # API Key input
    api_key = st.text_input("Google Gemini API Key", type="password")
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
        genai.configure(api_key=api_key)
    
    # Bot name
    bot_name = st.text_input("Bot Name", value=st.session_state.bot_name)
    if bot_name != st.session_state.bot_name:
        st.session_state.bot_name = bot_name
    
    # Model selection
    model_option = st.selectbox(
        "Select Gemini Model",
        ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"],
        index=["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"].index(st.session_state.model)
    )
    if model_option != st.session_state.model:
        st.session_state.model = model_option
    
    # Temperature slider
    temperature = st.slider(
        "Temperature (Creativity)",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.temperature,
        step=0.1,
        help="Higher values make output more creative, lower values make it more focused"
    )
    if temperature != st.session_state.temperature:
        st.session_state.temperature = temperature
    
    # Reset chat button
    if st.button("Reset Chat"):
        st.session_state.messages = []
        st.rerun()

# Main content area - System Prompt
st.header("System Prompt")
system_prompt = st.text_area(
    "Enter instructions for how your bot should behave:",
    height=400,
    value=st.session_state.system_prompt
)
if system_prompt != st.session_state.system_prompt:
    st.session_state.system_prompt = system_prompt

# Function to get response from Gemini
def get_gemini_response(prompt):
    try:
        # Add API key check
        if not api_key:
            return "Please enter your Google Gemini API Key in the sidebar to continue."
        
        # Prepare context with system prompt and chat history
        context = f"System Instructions: {st.session_state.system_prompt}\n\n"
        context += "Previous Messages:\n"
        for msg in st.session_state.messages[:-1]:  # Exclude the latest message
            context += f"{msg['role'].title()}: {msg['content']}\n"
        
        # Generate response
        model = genai.GenerativeModel(
            st.session_state.model, 
            generation_config={"temperature": st.session_state.temperature}
        )
        response = model.generate_content(f"{context}\n\nUser Query: {prompt}")
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# Chat interface
st.header(f"Test Your Bot: {st.session_state.bot_name}")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type a message to test your bot..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = get_gemini_response(prompt)
            st.markdown(response)
    
    # Add assistant response to chat
    st.session_state.messages.append({"role": "assistant", "content": response})

# Display current configuration
with st.expander("Current Configuration"):
    st.write(f"**Bot Name:** {st.session_state.bot_name}")
    st.write(f"**Model:** {st.session_state.model}")
    st.write(f"**Temperature:** {st.session_state.temperature}")
