import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import base64

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

if "previous_template" not in st.session_state:
    st.session_state.previous_template = "Basic Assistant"

if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = (
        "You are a helpful assistant named Gemini Assistant. "
        "You're friendly, concise, and informative. When answering questions, "
        "provide accurate information and be honest when you don't know something."
    )

if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7

if "model" not in st.session_state:
    st.session_state.model = "gemini-1.5-pro"

if "initial_prompts" not in st.session_state:
    st.session_state.initial_prompts = (
        "What can you help me with?\nHow does this assistant work?\nTell me about yourself."
    )

# Track which view is selected
if "selected_view" not in st.session_state:
    st.session_state.selected_view = "bot_builder"

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

    # --- Separator & toggle buttons for main view ---
    st.write("---")
    col_button1, col_button2 = st.columns(2)
    with col_button1:
        if st.button("Bot Builder"):
            st.session_state.selected_view = "bot_builder"
    with col_button2:
        if st.button("Prompt Guidance"):
            st.session_state.selected_view = "guidance"
    st.write("---")

    # Document upload section
    st.header("Reference Documents")
    uploaded_files = st.file_uploader(
        "Upload documents for context (PDF, DOCX, TXT)",
        accept_multiple_files=True
    )
    
    # Initialize document context in session state if not present
    if "document_context" not in st.session_state:
        st.session_state.document_context = ""
    
    # Process documents button
    if uploaded_files and st.button("Process Documents"):
        document_text = ""
        for file in uploaded_files:
            try:
                if file.name.endswith('.pdf'):
                    import PyPDF2
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        document_text += page.extract_text() + "\n"
                elif file.name.endswith('.docx'):
                    import docx
                    doc = docx.Document(file)
                    for para in doc.paragraphs:
                        document_text += para.text + "\n"
                else:  # Assume text file
                    document_text += file.getvalue().decode("utf-8") + "\n"
                
                document_text += f"\n--- End of {file.name} ---\n\n"
            except Exception as e:
                st.error(f"Error processing {file.name}: {e}")
        
        st.session_state.document_context = document_text
        st.success(f"Processed {len(uploaded_files)} document(s)")

    # Export Configuration
    st.header("Export Configuration")
    
    if st.button("Export Settings"):
        # Create settings dictionary
        settings = {
            "bot_name": st.session_state.bot_name,
            "temperature": st.session_state.temperature,
            "model": st.session_state.model
        }
        
        # Convert settings to JSON
        settings_json = json.dumps(settings, indent=2)
        
        # Create downloadable links
        st.markdown("### Download Configuration Files")
        
        # Settings JSON file
        settings_b64 = base64.b64encode(settings_json.encode()).decode()
        settings_href = f'<a href="data:application/json;base64,{settings_b64}" download="settings.json">Download settings.json</a>'
        st.markdown(settings_href, unsafe_allow_html=True)
        
        # System prompt file
        prompt_b64 = base64.b64encode(st.session_state.system_prompt.encode()).decode()
        prompt_href = f'<a href="data:text/plain;base64,{prompt_b64}" download="system_prompt.txt">Download system_prompt.txt</a>'
        st.markdown(prompt_href, unsafe_allow_html=True)

        # Custom initial prompts file
        sample_prompts = st.session_state.initial_prompts
        prompts_b64 = base64.b64encode(sample_prompts.encode()).decode()
        prompts_href = f'<a href="data:text/plain;base64,{prompts_b64}" download="initial_prompts.txt">Download initial_prompts.txt</a>'
        st.markdown(prompts_href, unsafe_allow_html=True)
    
    # Reset chat button
    if st.button("Reset Chat"):
        st.session_state.messages = []
        st.rerun()

# -----------------------
# Main Area: Conditional Views
# -----------------------

if st.session_state.selected_view == "bot_builder":
    # Bot Builder Content

    # Bot Name
    st.header("Bot Configuration")
    new_bot_name = st.text_input("Bot Name", value=st.session_state.bot_name)
    if new_bot_name != st.session_state.bot_name:
        st.session_state.bot_name = new_bot_name

    # (System Prompt header removed -- only the text area remains)

    # Define sample templates
    templates = {
        "Basic Assistant": """You are a helpful assistant named {bot_name}. You'
