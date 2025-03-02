# utils.py

import streamlit as st
import google.generativeai as genai
import json
import base64
import templates


def configure_gemini_api(api_key):
    """Configure the Gemini API with the provided key."""
    genai.configure(api_key=api_key)


def get_gemini_response(prompt):
    """Get a response from the Gemini API."""
    try:
        if "GOOGLE_API_KEY" not in st.session_state:
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


def render_document_uploader():
    """Render the document uploader section in the sidebar."""
    st.header("Reference Documents")
    uploaded_files = st.file_uploader(
        "Upload documents for context (PDF, DOCX, TXT)",
        accept_multiple_files=True
    )

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


def render_export_section():
    """Render the export configuration section in the sidebar."""
    st.header("Export Configuration")
    
    if st.button("Export Settings"):
        settings = {
            "bot_name": st.session_state.bot_name,
            "temperature": st.session_state.temperature,
            "model": st.session_state.model
        }
        settings_json = json.dumps(settings, indent=2)

        st.markdown("### Download Configuration Files")
        
        # settings.json
        settings_b64 = base64.b64encode(settings_json.encode()).decode()
        settings_href = f'<a href="data:application/json;base64,{settings_b64}" download="settings.json">Download settings.json</a>'
        st.markdown(settings_href, unsafe_allow_html=True)
        
        # system_prompt.txt
        prompt_b64 = base64.b64encode(st.session_state.system_prompt.encode()).decode()
        prompt_href = f'<a href="data:text/plain;base64,{prompt_b64}" download="system_prompt.txt">Download system_prompt.txt</a>'
        st.markdown(prompt_href, unsafe_allow_html=True)

        # initial_prompts.txt
        sample_prompts = st.session_state.initial_prompts
        prompts_b64 = base64.b64encode(sample_prompts.encode()).decode()
        prompts_href = f'<a href="data:text/plain;base64,{prompts_b64}" download="initial_prompts.txt">Download initial_prompts.txt</a>'
        st.markdown(prompts_href, unsafe_allow_html=True)


def render_bot_builder():
    """Render the Bot Builder view."""
    # "What is the name of your bot?"
    st.subheader("What is the name of your bot?")
    new_bot_name = st.text_input("", value=st.session_state.bot_name)
    if new_bot_name != st.session_state.bot_name:
        st.session_state.bot_name = new_bot_name

    # Choose a Template
    st.subheader("Choose a Template")
    template_names = templates.get_template_names()
    selected_template = st.selectbox(
        "",
        options=template_names,
        index=template_names.index("Basic Assistant") if "Basic Assistant" in template_names else 0
    )

    # Auto-populate system prompt based on template
    previous_template = st.session_state.previous_template

    if selected_template == "Punny Professor":
