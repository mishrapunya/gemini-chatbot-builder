import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import base64

st.set_page_config(page_title="Chatbot Builder", layout="wide")

load_dotenv()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "bot_name" not in st.session_state:  
    st.session_state.bot_name = "Gemini Assistant"
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

st.title("Chatbot Builder")
st.markdown("Configure and test your Gemini-powered chatbot with this builder interface.")

st.subheader("Give a name to your Bot")
new_bot_name = st.text_input("", value=st.session_state.bot_name)
if new_bot_name != st.session_state.bot_name:
    st.session_state.bot_name = new_bot_name
    
st.subheader("Set Your System Prompt (or choose a template)")
templates = {...} # Same template definitions as before

selected_template = st.selectbox("", options=list(templates.keys()), index=0)

# Auto-populate system prompt and bot name based on template
if selected_template == "Punny Professor":
    domain = st.text_input("Subject Domain", value="Science")
    education_level = st.selectbox(
        "Education Level",
        ["Elementary", "Middle School", "High School", "Undergraduate", "Graduate"]
    )
    prompt_text = templates[selected_template].format(
        domain=domain, education_level=education_level
    )
    if st.session_state.system_prompt != prompt_text:
        st.session_state.system_prompt = prompt_text
        st.session_state.bot_name = "Punny Professor"
            
elif selected_template == "Analogy Creator":
    domain = st.text_input("Subject Domain", value="Science")
    education_level = st.selectbox(
        "Education Level",
        ["Elementary", "Middle School", "High School", "Undergraduate", "Graduate"]
    )
    prompt_text = templates[selected_template].format(
        domain=domain, education_level=education_level
    )
    if st.session_state.system_prompt != prompt_text:
        st.session_state.system_prompt = prompt_text
        st.session_state.bot_name = "Analogy Creator"
        
elif selected_template == "Customer Support from Hell":
    company_name = st.text_input("Company Name", value="TechCorp") 
    product_type = st.text_input("Product Type", value="cloud software solutions")
    prompt_text = templates[selected_template].format(
        company_name=company_name, product_type=product_type
    )
    if st.session_state.system_prompt != prompt_text:
        st.session_state.system_prompt = prompt_text
        st.session_state.bot_name = "Customer Support"
            
else:  # Basic Assistant
    prompt_text = templates[selected_template].format(
        bot_name=st.session_state.bot_name
    )
    if st.session_state.system_prompt != prompt_text:
        st.session_state.system_prompt = prompt_text

expanded_view = st.toggle("Expanded View", value=False)
    
if expanded_view:
    system_prompt = st.text_area("", height=400, value=st.session_state.system_prompt)
else:
    system_prompt = st.text_area("", height=200, value=st.session_state.system_prompt)
        
if system_prompt != st.session_state.system_prompt:
    st.session_state.system_prompt = system_prompt
        
st.subheader("Suggested Initial Prompts")
initial_prompts = st.text_area(
    "Enter one prompt per line:",
    height=150,
    value=st.session_state.initial_prompts    
)
if initial_prompts != st.session_state.initial_prompts:
    st.session_state.initial_prompts = initial_prompts
        
st.subheader(f"Meet your {st.session_state.bot_name}!")
intro_prompt = st.session_state.initial_prompts.split('\n', 1)[0]
conversation_starter = get_gemini_response(intro_prompt)
st.markdown(conversation_starter)
        
st.subheader("Test Your Bot")

# Function to get Gemini response
def get_gemini_response(prompt):
    try:
        if not api_key:
            return "Please enter your Google Gemini API Key in the sidebar to continue."
        
        context = f"System Instructions: {st.session_state.system_prompt}\n\n"
        if st.session_state.document_context:
            context += f"Reference Information:\n{st.session_state.document_context}\n\n"
        context += "Previous Messages:\n"
        for msg in st.session_state.messages[:-1]:
            context += f"{msg['role'].title()}: {msg['content']}\n"
        
        model = genai.GenerativeModel(
            st.session_state.model,
            generation_config={"temperature": st.session_state.temperature}
        )
        response = model.generate_content(f"{context}\n\nUser Query: {prompt}")
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# Chat interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Type a message to test your bot..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = get_gemini_response(prompt)
            st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

# Sidebar
with st.sidebar:
    st.header("ChatBot Configuration")
    
    api_key = st.text_input("Google Gemini API Key", type="password")
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
        genai.configure(api_key=api_key)

    model_option = st.selectbox(
        "Select Gemini Model", 
        ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"],
        index=["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"].index(st.session_state.model)
    )
    if model_option != st.session_state.model:
        st.session_state.model = model_option
    
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
                else:  # assume text file
                    document_text += file.getvalue().decode("utf-8") + "\n"

                document_text += f"\n--- End of {file.name} ---\n\n"
            except Exception as e:
                st.error(f"Error processing {file.name}: {e}")

        st.session_state.document_context = document_text
        st.success(f"Processed {len(uploaded_files)} document(s)")

    st.header("Export Configuration")
    
    if st.button("Export Settings"):
        settings = {
            "bot_name": st.session_state.bot_name,
            "temperature": st.session_state.temperature,
            "model": st.session_state.model
        }
        settings_json = json.dumps(settings, indent=2)

        st.markdown("### Download Configuration Files")
        
        settings_b64 = base64.b64encode(settings_json.encode()).decode()
        settings_href = f'<a href="data:application/json;base64,{settings_b64}" download="settings.json">Download settings.json</a>'
        st.markdown(settings_href, unsafe_allow_html=True)
        
        prompt_b64 = base64.b64encode(st.session_state.system_prompt.encode()).decode()
        prompt_href = f'<a href="data:text/plain;base64,{prompt_b64}" download="system_prompt.txt">Download system_prompt.txt</a>'
        st.markdown(prompt_href, unsafe_allow_html=True)

        sample_prompts = st.session_state.initial_prompts
        prompts_b64 = base64.b64encode(sample_prompts.encode()).decode()
        prompts_href = f'<a href="data:text/plain;base64,{prompts_b64}" download="initial_prompts.txt">Download initial_prompts.txt</a>'
        st.markdown(prompts_href, unsafe_allow_html=True)

    if st.button("Reset Chat"):
        st.session_state.messages = []
        st.rerun()
