import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import base64

# Page configuration
st.set_page_config(
    page_title="Chatbot Builder",
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

# Apply custom CSS for spacing adjustments
st.markdown(
    """
    <style>
        h2, h3 {
            margin-bottom: 5px !important;
        }
        .stTextInput, .stSelectbox, .stSlider, .stTextArea, .stFileUploader {
            margin-top: 0px !important;
            margin-bottom: 10px !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Title & description
st.title("Chatbot Builder")
st.markdown("Configure and test your Gemini-powered chatbot with this builder interface.")

# Sidebar Configuration
with st.sidebar:
    st.header("ChatBot Configuration")

    # Google Gemini API Key
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
        step=0.1
    )
    if temperature != st.session_state.temperature:
        st.session_state.temperature = temperature

    # Navigation
    st.header("Navigation")
    view = st.selectbox("", ["Bot Builder", "Prompt Guidance"], index=0, label_visibility="collapsed")

    # Reference Documents
    st.header("Reference Documents")
    uploaded_files = st.file_uploader(
        "Upload documents for context (PDF, DOCX, TXT)",
        accept_multiple_files=True
    )

    if "document_context" not in st.session_state:
        st.session_state.document_context = ""

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

# Main View
if view == "Bot Builder":

    # "What is the name of your bot?"
    st.subheader("What is the name of your bot?")
    new_bot_name = st.text_input("", value=st.session_state.bot_name)
    if new_bot_name != st.session_state.bot_name:
        st.session_state.bot_name = new_bot_name

    # Combined Template and System Prompt section
    st.subheader("Set Your System Prompt (or choose a template)")

    templates = {
        "Basic Assistant": "You are a helpful assistant named {bot_name}.",
        "Punny Professor": "You are the Punny Professor, a witty and knowledgeable educator.",
        "Analogy Creator": "You are an Analogy Creator, an expert at crafting insightful analogies.",
        "Customer Support from Hell": "You are a Customer Support Representative from Hell."
    }

    selected_template = st.selectbox("", options=list(templates.keys()), index=0)

    # Auto-populate system prompt
    prompt_text = templates[selected_template].format(bot_name=st.session_state.bot_name)
    if st.session_state.system_prompt != prompt_text:
        st.session_state.system_prompt = prompt_text

    system_prompt = st.text_area("", height=200, value=st.session_state.system_prompt)
    if system_prompt != st.session_state.system_prompt:
        st.session_state.system_prompt = system_prompt

    # Suggested Initial Prompts
    st.subheader("Suggested Initial Prompts")
    initial_prompts = st.text_area("Enter one prompt per line:", height=150, value=st.session_state.initial_prompts)
    if initial_prompts != st.session_state.initial_prompts:
        st.session_state.initial_prompts = initial_prompts

    # Chat Interface
    st.subheader("Test Your Bot")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Type a message to test your bot..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = f"Simulated response for: {prompt}"
                st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

else:
    # === PROMPT GUIDANCE VIEW ===
    st.markdown("## Elements of an Effective System Prompt")
    guidance_content = """
    **1. Role / Persona**  
    Define the chatbot's identity and expertise.
    
    **2. Purpose / Objective**  
    State the chatbot's primary function.
    
    **3. Context / Background**  
    Provide situational information.
    
    **4. Style and Tone Guidelines**  
    Specify language usage and formality.
    
    **5. Output Format / Structure**  
    Outline response formatting.
    
    **6. Constraints and Prohibitions**  
    List restricted topics or behaviors.
    
    **7. Disclaimers**  
    Include mandatory disclaimers.
    
    **8. Stay in Character**  
    Ensure adherence to role and instructions.
    """
    st.markdown(guidance_content)
