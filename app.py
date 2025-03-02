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
    st.session_state.system_prompt = "You are a helpful assistant named Gemini Assistant. You're friendly, concise, and informative. When answering questions, provide accurate information and be honest when you don't know something."

if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7

if "model" not in st.session_state:
    st.session_state.model = "gemini-1.5-pro"

if "initial_prompts" not in st.session_state:
    st.session_state.initial_prompts = "What can you help me with?\nHow does this assistant work?\nTell me about yourself."

if "view" not in st.session_state:
    st.session_state.view = "bot_builder"
    
# Guidance Content
PROMPT_GUIDANCE = """
### Elements of an Effective System Prompt

#### 1. Role / Persona
Define the chatbot's identity, expertise, and overall demeanor.
*Example: "You are a knowledgeable customer support specialist for a software company."*

#### 2. Purpose / Objective
State the chatbot's primary function and intended goals.
*Example: "Your purpose is to help users troubleshoot technical issues and guide them to appropriate resources."*

#### 3. Context / Background
Provide any relevant situational or organizational information.
*Example: "You represent TechCorp, which offers cloud-based productivity software."*

#### 4. Style and Tone Guidelines
Specify language usage, formality level, and stylistic preferences.
*Example: "Maintain a professional but friendly tone. Use simple language without jargon when possible."*

#### 5. Output Format / Structure
Outline how responses should be organized or formatted.
*Example: "For troubleshooting, present steps in a numbered list. For complex explanations, use bullet points."*

#### 6. Constraints and Prohibitions
List topics, behaviors, or actions the bot must avoid.
*Example: "Do not provide specific pricing information. Refer pricing questions to our website."*

#### 7. Disclaimers
Include any mandatory disclaimers.
*Example: "Always clarify that your suggestions are not a substitute for professional technical support."*

#### 8. Stay in Character
Reinforce adherence to the defined role and instructions.
*Example: "Always respond as a customer support specialist, not as an AI."*
"""

# Title and description
st.title("🤖 Gemini Chatbot Builder")
st.markdown("Configure and test your Gemini-powered chatbot with this builder interface.")

# Create tabs
tab1, tab2, tab3 = st.tabs(["Configuration", "Prompt Guidance", "Bot Testing"])

# Sidebar Configuration
with tab1:
    st.header("API Configuration")
    
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

    # Divider for visual separation
    st.divider()

    # Toggle view button
    if st.session_state.view == "bot_builder":
        if st.button("📘 View Prompt Writing Guidance"):
            st.session_state.view = "guidance"
    else:
        if st.button("🤖 Back to Bot Builder"):
            st.session_state.view = "bot_builder"

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

        # Custom initial prompts file from user input
        sample_prompts = st.session_state.initial_prompts
        prompts_b64 = base64.b64encode(sample_prompts.encode()).decode()
        prompts_href = f'<a href="data:text/plain;base64,{prompts_b64}" download="initial_prompts.txt">Download initial_prompts.txt</a>'
        st.markdown(prompts_href, unsafe_allow_html=True)
    
    # Reset chat button
    if st.button("Reset Chat"):
        st.session_state.messages = []
        st.rerun()

# Prompt Guidance Tab
with tab2:
    st.header("System Prompt Guidance")
    st.markdown(PROMPT_GUIDANCE)

# Bot Testing and Configuration Tab
# Check the current view
if st.session_state.view == "bot_builder":
    # Bot Name
    st.header("Bot Configuration")
    new_bot_name = st.text_input("Bot Name", value=st.session_state.bot_name)
    if new_bot_name != st.session_state.bot_name:
        st.session_state.bot_name = new_bot_name

    # Keep all subsequent existing code (template selection, system prompt, etc.) 
    # This includes:
    # - Template selection section
    # - Template parameters
    # - System prompt text area
    # - Initial prompts section
    # Essentially, all the existing code that was previously inside this tab

else:
    # Guidance view
    st.header("Prompt Writing Guidance")
    st.markdown("""
    ### Elements of an Effective System Prompt

    #### 1. Role / Persona
    Define the chatbot's identity, expertise, and overall demeanor.
    *Example: "You are a knowledgeable customer support specialist for a software company."*

    #### 2. Purpose / Objective
    State the chatbot's primary function and intended goals.
    *Example: "Your purpose is to help users troubleshoot technical issues and guide them to appropriate resources."*

    #### 3. Context / Background
    Provide any relevant situational or organizational information.
    *Example: "You represent TechCorp, which offers cloud-based productivity software."*

    #### 4. Style and Tone Guidelines
    Specify language usage, formality level, and stylistic preferences.
    *Example: "Maintain a professional but friendly tone. Use simple language without jargon when possible."*

    #### 5. Output Format / Structure
    Outline how responses should be organized or formatted.
    *Example: "For troubleshooting, present steps in a numbered list. For complex explanations, use bullet points."*

    #### 6. Constraints and Prohibitions
    List topics, behaviors, or actions the bot must avoid.
    *Example: "Do not provide specific pricing information. Refer pricing questions to our website."*

    #### 7. Disclaimers
    Include any mandatory disclaimers.
    *Example: "Always clarify that your suggestions are not a substitute for professional technical support."*

    #### 8. Stay in Character
    Reinforce adherence to the defined role and instructions.
    *Example: "Always respond as a customer support specialist, not as an AI."*
    """)
    initial_prompts = st.text_area(
        "Enter one prompt per line:",
        height=150,
        value=st.session_state.initial_prompts
    )

    if initial_prompts != st.session_state.initial_prompts:
        st.session_state.initial_prompts = initial_prompts

def get_gemini_response(prompt):
    try:
        # Add API key check
        if not api_key:
            return "Please enter your Google Gemini API Key in the sidebar to continue."
        
        # Prepare context with system prompt, document context, and chat history
        context = f"System Instructions: {st.session_state.system_prompt}\n\n"
        
        # Add document context if available
        if st.session_state.document_context:
            context += f"Reference Information:\n{st.session_state.document_context}\n\n"
        
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

# Display current configuration
with st.expander("Current Configuration"):
    st.write(f"**Bot Name:** {st.session_state.bot_name}")
    st.write(f"**Model:** {st.session_state.model}")
    st.write(f"**Temperature:** {st.session_state.temperature}")

# Add chat interface to the last tab
with tab3:
    # Chat interface continuation
    st.header("Test Your Bot")

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
