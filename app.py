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
        
        # Sample initial prompts file (empty template)
        sample_prompts = "What services do you offer?\nHow can I get started?\nTell me more about your company."
        prompts_b64 = base64.b64encode(sample_prompts.encode()).decode()
        prompts_href = f'<a href="data:text/plain;base64,{prompts_b64}" download="initial_prompts.txt">Download initial_prompts.txt</a>'
        st.markdown(prompts_href, unsafe_allow_html=True)
    
    # Reset chat button
    if st.button("Reset Chat"):
        st.session_state.messages = []
        st.rerun()

# Bot Name in main panel
st.header("Bot Configuration")
new_bot_name = st.text_input("Bot Name", value=st.session_state.bot_name)
if new_bot_name != st.session_state.bot_name:
    st.session_state.bot_name = new_bot_name

# Main content area - System Prompt with expanded view option
st.header("System Prompt")

# Define sample templates
templates = {
    "Basic Assistant": """You are a helpful assistant named {bot_name}. You're friendly, concise, and informative. When answering questions, provide accurate information and be honest when you don't know something. Use examples when they help explain concepts.""",
    
    "Punny Professor": """You are the Punny Professor, a witty and knowledgeable educator who explains concepts using clever puns and wordplay.

Your purpose is to create educational jokes and puns about {domain} topics that are appropriate for {education_level} students.

When given a topic, you should:
1. Explain the concept clearly and accurately
2. Create 2-3 puns or jokes related to the topic
3. Ensure jokes are appropriate for the educational level specified
4. Explain the wordplay if it involves advanced terminology

Your tone should be enthusiastic, warm, and slightly corny - like a beloved teacher who uses humor to make learning memorable.

Always maintain scientific/educational accuracy while making the content engaging and fun.""",
    
    "Analogy Creator": """You are an Analogy Creator, an expert at crafting insightful analogies and metaphors to explain complex concepts.

Your purpose is to help educators explain difficult {domain} concepts by creating clear, relatable analogies tailored to {education_level} students.

When a concept is presented:
1. First, briefly explain the concept in clear, straightforward terms
2. Create 3-4 different analogies for the concept, ranging from simple to more nuanced
3. For each analogy, explain how specific elements map to the original concept
4. Suggest ways the teacher could extend the analogy in classroom discussions

Your analogies should relate to everyday experiences students would understand and should avoid overly technical or obscure references.

Balance accuracy with simplicity, ensuring that the analogy doesn't introduce misconceptions.""",
    
    "Customer Support from Hell": """You are a Customer Support Representative from Hell for {company_name}, which allegedly offers {product_type}.

Your purpose is to appear helpful while being absolutely useless to customers with questions or issues.

Your support style should:
1. Use excessive technical jargon that obscures rather than clarifies
2. Provide circular solutions ("Have you tried turning it off and on again?" regardless of the issue)
3. Blame the customer subtly for their problems
4. Redirect customers to different departments unnecessarily
5. Respond with obviously scripted answers that don't address the specific issue

Your tone should be artificially cheerful with thinly-veiled impatience. Use corporate buzzwords excessively.

Always add this disclaimer: "Your satisfaction is our top priority! This call may be monitored for quality assurance purposes."

Remember to remain in character as the world's most frustrating customer support agent."""
}

# Set default template for display
template = templates["Basic Assistant"]

# Add guidance for creating effective system prompts
with st.expander("Guidance for Creating Effective System Prompts", expanded=False):
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
    
    ### Sample System Prompt Template
    ```
    """ + template + """
    ```
    """)

# Template selection section
st.subheader("Choose a Template")
selected_template = st.selectbox(
    "Select a starting template:",
    options=list(templates.keys()),
    index=0
)

# Show template parameters and auto-populate based on selection
if selected_template == "Punny Professor":
    col1, col2 = st.columns(2)
    with col1:
        domain = st.text_input("Subject Domain", value="Science")
    with col2:
        education_level = st.selectbox("Education Level", ["Elementary", "Middle School", "High School", "Undergraduate", "Graduate"])
    
    # Auto-populate when parameters change
    prompt_text = templates[selected_template].format(domain=domain, education_level=education_level)
    if st.session_state.system_prompt != prompt_text:
        st.session_state.system_prompt = prompt_text
        st.session_state.bot_name = "Punny Professor"
        st.session_state.initial_prompts = f"Can you explain {domain} in a funny way?\nMake a pun about {domain}.\nWhat's a joke about {domain} suitable for {education_level} students?"

elif selected_template == "Analogy Creator":
    col1, col2 = st.columns(2)
    with col1:
        domain = st.text_input("Subject Domain", value="Science")
    with col2:
        education_level = st.selectbox("Education Level", ["Elementary", "Middle School", "High School", "Undergraduate", "Graduate"])
    
    # Auto-populate when parameters change
    prompt_text = templates[selected_template].format(domain=domain, education_level=education_level)
    if st.session_state.system_prompt != prompt_text:
        st.session_state.system_prompt = prompt_text
        st.session_state.bot_name = "Analogy Creator"
        st.session_state.initial_prompts = f"Can you explain {domain} using an analogy?\nHow would you describe {domain} to a {education_level} student?\nWhat's a good metaphor for explaining {domain}?"

elif selected_template == "Customer Support from Hell":
    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input("Company Name", value="TechCorp")
    with col2:
        product_type = st.text_input("Product Type", value="cloud software solutions")
    
    # Auto-populate when parameters change
    prompt_text = templates[selected_template].format(company_name=company_name, product_type=product_type)
    if st.session_state.system_prompt != prompt_text:
        st.session_state.system_prompt = prompt_text
        st.session_state.bot_name = "Customer Support"
        st.session_state.initial_prompts = f"I need help with my {product_type}.\nHow do I contact a manager?\nWhy is your {product_type} not working?"

else:  # Basic Assistant
    # Auto-populate
    prompt_text = templates[selected_template].format(bot_name=st.session_state.bot_name)
    if st.session_state.system_prompt != prompt_text and selected_template != previous_template:
        st.session_state.system_prompt = prompt_text
        # Keep existing bot name
        st.session_state.initial_prompts = "What can you help me with?\nHow does this assistant work?\nTell me about yourself."

# Store the previous template selection
if "previous_template" not in st.session_state:
    st.session_state.previous_template = selected_template
previous_template = st.session_state.previous_template
if previous_template != selected_template:
    st.session_state.previous_template = selected_template


# Expanded view toggle
st.subheader("System Prompt")
expanded_view = st.toggle("Expanded View", value=False)

if expanded_view:
    # Full-width expanded view for the system prompt
    system_prompt = st.text_area(
        "Enter instructions for how your bot should behave:",
        height=600,
        value=st.session_state.system_prompt
    )
else:
    # Normal view
    system_prompt = st.text_area(
        "Enter instructions for how your bot should behave:",
        height=400,
        value=st.session_state.system_prompt
    )

if system_prompt != st.session_state.system_prompt:
    st.session_state.system_prompt = system_prompt

# Initial Prompts Section
st.header("Suggested Initial Prompts")
st.markdown("These are the questions/prompts that will be suggested to users in the production app.")

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


# Chat interface
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

# Display current configuration
with st.expander("Current Configuration"):
    st.write(f"**Bot Name:** {st.session_state.bot_name}")
    st.write(f"**Model:** {st.session_state.model}")
    st.write(f"**Temperature:** {st.session_state.temperature}")
