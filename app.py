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
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Chatbot Builder powered by Gemini"
    }
)

# Apply theme
st.markdown("""
    <style>
    :root {
        --primary-color: #2563EB;
        --background-color: #FFFFFF;
        --secondary-background-color: #F8FAFC;
        --text-color: #374151;
        --font: "sans-serif";
    }
    </style>
    """, unsafe_allow_html=True)

# Apply balanced spacing CSS
st.markdown("""
<style>
/* Header styling with better colors */
h1, h2, h3, .stSubheader {
    color: #2563EB !important;
    margin-bottom: 0.2rem !important;
    padding-bottom: 0.1rem !important;
}

/* Add some space at the top to prevent title cutoff */
.main .block-container {
    padding-top: 2rem !important;
}

/* Target the specific gap between header and input */
label[data-testid="stText"], .stMarkdown p {
    margin-bottom: 0.2rem !important;
    padding-bottom: 0.1rem !important;
    line-height: 1.3 !important;
}

/* Target spaces around text inputs and areas */
.stTextInput div, .stTextArea div {
    padding-top: 0.2rem !important;
    margin-top: 0.1rem !important;
}

/* Reduce caption spacing but keep it readable */
small {
    margin-top: 0.1rem !important;
    margin-bottom: 0.1rem !important;
    line-height: 1.2 !important;
}

/* More balanced space between sections */
section > div {
    padding-top: 0.7rem !important;
    padding-bottom: 0.7rem !important;
}

/* Chat message styling */
.stChatMessage[data-testid="stChatMessageUser"] {
    background-color: #EFF6FF !important;
}

.stChatMessage[data-testid="stChatMessageAssistant"] {
    background-color: #F8FAFC !important;
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

    # Add space before footer with reduced gap
    st.sidebar.markdown("<hr style='margin-bottom: 5px;'>", unsafe_allow_html=True)
    
    # Footer with copyright, attribution, and link
    st.sidebar.markdown("""
    <div style="text-align: center; color: #718096; font-size: 0.8rem;">
        © <a href="https://punyamishra.com" target="_blank" style="color: #2563EB; text-decoration: none;">punyamishra</a> 2025 <br>
        Chatbot builder designed and created by Punya Mishra,<br>with lots of help from Claude and ChatGPT<br><br>
        <span style="font-size: 0.7rem;">Available for use and modification with attribution to the original creator.</span>
    </div>
    """, unsafe_allow_html=True)

# 7. Main area: Navigation between Bot Builder and Prompt Guidance
if st.session_state.current_view == "Bot Builder":
    utils.render_bot_builder()
else:
    # Load and display the prompt guidance content from the markdown file
    with open("prompt_guidance.md", "r") as f:
        guidance_content = f.read()
    st.markdown(guidance_content)
