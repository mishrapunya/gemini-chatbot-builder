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
    """Render the Bot Builder view with improved layout."""
    # 1. "Give a name to your Bot" section
    st.subheader("Give a name to your Bot")
    new_bot_name = st.text_input("", value=st.session_state.bot_name)
    if new_bot_name != st.session_state.bot_name:
        st.session_state.bot_name = new_bot_name
        
    # 2. "Set Your System Prompt (or choose a template)" section
    st.subheader("Set Your System Prompt (or choose a template)")
    
    # Template selection
    template_names = templates.get_template_names()
    selected_template = st.selectbox(
        "Choose a template:",
        options=template_names,
        index=template_names.index("Basic Assistant") if "Basic Assistant" in template_names else 0
    )

    # Template-specific fields
    if selected_template == "Punny Professor":
        col1, col2 = st.columns(2)
        with col1:
            domain = st.text_input("Subject Domain", value="Science")
        with col2:
            education_level = st.selectbox(
                "Education Level",
                ["Elementary", "Middle School", "High School", "Undergraduate", "Graduate"]
            )
        
        prompt_text = templates.get_template_text(selected_template, domain=domain, education_level=education_level)
        if st.session_state.system_prompt != prompt_text:
            st.session_state.system_prompt = prompt_text
            st.session_state.bot_name = "Punny Professor"
            st.session_state.initial_prompts = templates.get_default_initial_prompts(
                selected_template, domain=domain, education_level=education_level
            )

    elif selected_template == "Analogy Creator":
        col1, col2 = st.columns(2)
        with col1:
            domain = st.text_input("Subject Domain", value="Science")
        with col2:
            education_level = st.selectbox(
                "Education Level",
                ["Elementary", "Middle School", "High School", "Undergraduate", "Graduate"]
            )
        
        prompt_text = templates.get_template_text(selected_template, domain=domain, education_level=education_level)
        if st.session_state.system_prompt != prompt_text:
            st.session_state.system_prompt = prompt_text
            st.session_state.bot_name = "Analogy Creator"
            st.session_state.initial_prompts = templates.get_default_initial_prompts(
                selected_template, domain=domain, education_level=education_level
            )

    elif selected_template == "Customer Support from Hell":
        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input("Company Name", value="TechCorp")
        with col2:
            product_type = st.text_input("Product Type", value="cloud software solutions")
        
        prompt_text = templates.get_template_text(selected_template, company_name=company_name, product_type=product_type)
        if st.session_state.system_prompt != prompt_text:
            st.session_state.system_prompt = prompt_text
            st.session_state.bot_name = "Customer Support"
            st.session_state.initial_prompts = templates.get_default_initial_prompts(
                selected_template, product_type=product_type
            )

    else:  # Basic Assistant
        prompt_text = templates.get_template_text(selected_template, bot_name=st.session_state.bot_name)
        if (st.session_state.system_prompt != prompt_text
            and selected_template != st.session_state.previous_template):
            st.session_state.system_prompt = prompt_text
            st.session_state.initial_prompts = templates.get_default_initial_prompts(selected_template)

    # Store template selection
    if st.session_state.previous_template != selected_template:
        st.session_state.previous_template = selected_template

    # 3. Expanded View toggle
    expanded_view = st.toggle("Expanded View", value=False)
    st.caption("Edit your system prompt below:")

    # 4. System Prompt text area
    if expanded_view:
        system_prompt = st.text_area(
            "",
            height=600,
            value=st.session_state.system_prompt
        )
    else:
        system_prompt = st.text_area(
            "",
            height=200,
            value=st.session_state.system_prompt
        )
    if system_prompt != st.session_state.system_prompt:
        st.session_state.system_prompt = system_prompt

    # 5. Suggested Initial Prompts
    st.subheader("Suggested Initial Prompts")
    st.caption("These prompts will help users understand how to interact with your bot")
    initial_prompts = st.text_area(
        "Enter one prompt per line:",
        height=150,
        value=st.session_state.initial_prompts
    )
    if initial_prompts != st.session_state.initial_prompts:
        st.session_state.initial_prompts = initial_prompts

    # 6. Chat interface
    st.subheader("Test Your Bot")
    st.caption("Try out your bot configuration with sample queries")
    st.markdown("---")
    render_chat_interface()

def render_chat_interface():
    """Render the chat interface for testing the bot."""
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
                response = get_gemini_response(prompt)
                st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})


def render_prompt_guidance():
    """Render the Prompt Guidance view."""
    st.markdown("## Elements of an Effective System Prompt")
    guidance_content = """
    
    **1. Role / Persona**  
    Define the chatbot's identity, expertise, and overall demeanor.
    
    **2. Purpose / Objective**  
    State the chatbot's primary function and intended goals.
    
    **3. Context / Background**  
    Provide any relevant situational or organizational information.
    
    **4. Style and Tone Guidelines**  
    Specify language usage, formality level, and stylistic preferences.
    
    **5. Output Format / Structure**  
    Outline how responses should be organized or formatted.
    
    **6. Constraints and Prohibitions**  
    List topics, behaviors, or actions the bot must avoid.
    
    **7. Disclaimers**  
    Include any mandatory disclaimers.
    
    **8. Stay in Character**  
    Reinforce adherence to the defined role and instructions.
    """
    st.markdown(guidance_content)
