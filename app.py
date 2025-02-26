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
    bot_name = st.text_input("Bot Name", value="Gemini Assistant")
    
    # Model selection
    model_option = st.selectbox(
        "Select Gemini Model",
        ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"]
    )
    
    # Temperature slider
    temperature = st.slider(
        "Temperature (Creativity)",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Higher values make output more creative, lower values make it more focused"
    )

# Main content area - placeholder for now
st.header("System Prompt")
system_prompt = st.text_area(
    "Enter instructions for how your bot should behave:",
    height=400,
    value="You are a helpful assistant named Gemini Assistant. You're friendly, concise, and informative. When answering questions, provide accurate information and be honest when you don't know something."
)

# Placeholder for chat interface
st.header("Test Your Bot")
st.info("Chat interface will appear here in the next step.")

# Display current configuration
st.header("Current Configuration")
st.write(f"**Bot Name:** {bot_name}")
st.write(f"**Model:** {model_option}")
st.write(f"**Temperature:** {temperature}")
