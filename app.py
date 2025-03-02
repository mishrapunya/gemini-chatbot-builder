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

st.title("Chatbot Builder")
st.markdown("Configure and test your Gemini-powered chatbot with this builder interface.")

st.subheader("Give a name to your Bot")
new_bot_name = st.text_input("", value=st.session_state.bot_name)
if new_bot_name != st.session_state.bot_name:
    st.session_state.bot_name = new_bot_name

st.subheader("Set Your System Prompt (or choose a template)")

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

selected_template = st.selectbox("", options=list(templates.keys()), index=0)
previous_template = st.session_state.previous_template

# Auto-populate system prompt and suggested initial prompts based on template
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
        st.session_state.initial_prompts = (
            f"Can you explain {domain} in a funny way?\n"
            f"Make a pun about {domain}.\n"
            f"What's a joke about {domain} suitable for {education_level} students?"
        )
        
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
        st.session_state.initial_prompts = (
            f"Can you explain {domain} using an analogy?\n"
            f"How would you describe {domain} to a {education_level} student?\n"
            f"What's a good metaphor for explaining {domain}?"  
        )
        
elif selected_template == "Customer Support from Hell":
    company_name = st.text_input("Company Name", value="TechCorp")
    product_type = st.text_input("Product Type", value="cloud software solutions") 
    prompt_text = templates[selected_template].format(
        company_name=company_name, product_type=product_type
    )
    if st.session_state.system_prompt != prompt_text:
        st.session_state.system_prompt = prompt_text
        st.session_state.bot_name = "Customer Support"
        st.session_state.initial_prompts = (
            f"I need help with my {product_type}.\n"
            f"How do I contact a manager?\n" 
            f"Why is your {product_type} not working?"
        )
        
else:  # Basic Assistant
    prompt_text = templates[selected_template].format(
        bot_name=st.session_state.bot_name
    )
    if (st.session_state.system_prompt != prompt_text
        and selected_template != previous_template):
        st.session_state.system_prompt = prompt_text
        st.session_state.initial_prompts = (
            "What can you help me with?\nHow does this assistant work?\nTell me about yourself."
        )

if "previous_template" not in st.session_state:
    st.session_state.previous_template = selected_template  
if previous_template != selected_template:
    st.session_state.previous_template = selected_template

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
        
st.subheader(f"Meet {st.session_state.bot_name}!")
intro_prompt = st.session_state.initial_prompts.split('\n')[0]
conversation_starter = get_gemini_response(intro_prompt)
st.markdown(conversation_starter)

    # Chat interface
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

else:
    #
    # === PROMPT GUIDANCE VIEW ===
    #
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
