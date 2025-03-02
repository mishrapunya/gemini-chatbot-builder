# app.py

import streamlit as st
import os
from dotenv import load_dotenv

# Import our custom modules
import templates
import utils

# 1. Page configuration
st.set_page_config(
    page_title="Chatbot Builder",
    layout="wide"
)

# Apply custom CSS directly
st.markdown("""
<style>
/* Global spacing adjustments */
.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 1.5rem;
}

/* More cohesive typography */
p, div, span {
    color: #374151;
}

/* Header styling with better colors and reduced spacing */
h1 {
    color: #1E40AF;
    font-size: 2rem;
    margin-bottom: 0.5rem;
}

h2 {
    color: #1E3A8A;
    font-size: 1.7rem;
    margin-top: 1rem;
    margin-bottom: 0.4rem;
}

h3, .stSubheader {
    color: #2563EB;
    font-size: 1.3rem;
    font-weight: 600;
    margin-top: 0.8rem;
    margin-bottom: 0.3rem;
}

/* Reduce spacing between elements */
.stTextInput, .stTextArea, .stSelectbox {
    margin-top: 0.2rem !important;
    margin-bottom: 0.6rem !important;
}

/* Form element styling */
input, select, button {
    border-radius: 0.375rem !important;
}

.stTextArea textarea {
    border-radius: 0.375rem !important;
    border-color: #CBD5E1 !important;
    padding: 0.75rem !important;
    background-color: #F9FAFB !important;
}

/* Sidebar styling */
.sidebar .stButton > button {
    width: 100%;
    margin-top: 0.5rem;
}

/* Chat interface styling */
.stChatMessage {
    padding: 0.75rem !important;
    border-radius: 0.5rem !important;
    margin-bottom: 0.75rem !important;
}

.stChatMessage[data-testid="stChatMessageUser"] {
    background-color: #EFF6FF !important;
}

.stChatMessage[data-testid="stChatMessageAssistant"] {
    background-color: #F8FAFC !important;
}

/* Caption styling */
.css-1vencpc, .css-pxxe24 {
    margin-top: 0 !important;
    margin-bottom: 0.3rem !important;
}

/* Toggle switch fix */
.stToggle {
    margin-bottom: 0.3rem !important;
}

/* Navigation styling */
.stRadio > div {
    margin-top: 0.2rem !important;
    margin-bottom: 0.2rem !important;
}

/* Export link styling */
a[download] {
    display: block;
    margin: 0.4rem 0;
    padding: 0.5rem;
    background-color: #F1F5F9;
    border-radius: 0.375rem;
    text-decoration: none;
    text-align: center;
    color: #2563EB;
}

a[download]:hover {
    background-color: #E2E8F0;
}

/* Divider styling */
hr {
    margin-top: 1.2rem !important;
    margin-bottom: 1.2rem !important;
    border-color: #E2E8F0 !important;
}

/* Tooltip styling */
div[data-baseweb="tooltip"] {
    background-color: #334155 !important;
    border-radius: 0.25rem !important;
}

/* Prompt field styling */
div[data-testid="stForm"] {
    border: none !important;
    padding: 0 !important;
}
</style>
""", unsafe_allow_html=True)


# 3. Load environment variables
load_dotenv()

# 4. Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "bot_name" not in st.session_state:
    st.session_state.bot_name = "Gemini Assistant"

if "previous_template" not in st.session_state:
    st.session_state.previous_template = "Basic Assistant"

if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = templates.get_template_text("Basic Assistant", bot_name="Gemini Assistant")

if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7

if "model" not in st.session_state:
    st.session_state.model = "gemini-1.5-pro"

if "initial_prompts" not in st.session_state:
    st.session_state.initial_prompts = templates.get_default_initial_prompts("Basic Assistant")

if "document_context" not in st.session_state:
    st.session_state.document_context = ""

if "current_view" not in st.session_state:
    st.session_state.current_view = "Bot Builder"

# 5. Title & top description - ONLY shown in Bot Builder mode
if st.session_state.current_view == "Bot Builder":
    st.title("Chatbot Builder")
    st.markdown("Configure and test your Gemini-powered chatbot with this builder interface.")

# 6. Sidebar for configuration
with st.sidebar:
    st.header("ChatBot Configuration")
    
    # Google Gemini API Key
    api_key = st.text_input("Google Gemini API Key", type="password")
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
        utils.configure_gemini_api(api_key)
        # Store the API key in session state for later use
        st.session_state["GOOGLE_API_KEY"] = api_key

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
        help="Higher values make output more creative; lower values make it more focused"
    )
    if temperature != st.session_state.temperature:
        st.session_state.temperature = temperature

    # Navigation header and radio buttons that look like links
    st.header("Navigation")
    
    # Create radio buttons with horizontal orientation to look like links
    view = st.radio(
        "",
        ["Bot Builder", "Prompt Guide"],
        horizontal=True,
        label_visibility="collapsed",
        index=0 if st.session_state.current_view == "Bot Builder" else 1
    )
    
    # Update the current view based on selection
    if view == "Bot Builder":
        st.session_state.current_view = "Bot Builder"
    elif view == "Prompt Guide":
        st.session_state.current_view = "Prompt Guidance"
    
    # Reference Documents
    utils.render_document_uploader()

    # Export Configuration
    utils.render_export_section()

    # Reset chat
    if st.button("Reset Chat"):
        st.session_state.messages = []
        st.rerun()

# 7. Main area: Navigation between Bot Builder and Prompt Guidance
if st.session_state.current_view == "Bot Builder":
    utils.render_bot_builder()
else:
    # Load and display the prompt guidance content from the markdown file
    with open("prompt_guidance.md", "r") as f:
        guidance_content = f.read()
    st.markdown(guidance_content)
