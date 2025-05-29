import streamlit as st
import google.generativeai as genai
from bs4 import BeautifulSoup
import requests
import warnings
from streamlit_option_menu import option_menu
from streamlit_extras.mention import mention
from utils import extract_text_from_pdf, create_chunks, SimpleChromaDB
import tempfile
warnings.filterwarnings("ignore")
import os
from dotenv import load_dotenv

load_dotenv()
warnings.filterwarnings("ignore")

api_key = os.getenv('api_key')

# Initialize ChromaDB manager
if 'chroma_db' not in st.session_state:
    st.session_state.chroma_db = SimpleChromaDB()

generation_config = {
    "temperature": 0.1,  #  lower temperature for more focused responses
    "top_p": 0.85,
    "top_k": 40,
    "max_output_tokens": 32768,
}
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=generation_config,
)

# Define a system prompt on what does it do
SYSTEM_PROMPT = (
    "You are Knetsu, a kind and emotionally intelligent AI that ONLY gives advice about love, relationships, dating, "
    "heartbreak, or crushes. If the user asks something unrelated (like coding, math, science, tech, etc.), friendly reply: "
    "'I'm here only to talk about love and relationships. 💖'\n"
    "Do NOT attempt to answer off-topic questions or relate them to love. Just decline and do some light-hearted banter."
)

st.set_page_config(page_title="Introduction to Streamlit and GEMINI API", page_icon="", layout="wide")

# Session state initialization
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []


with st.sidebar:
    # If API key is not in environment, allow manual input
    if not api_key:
        api_key = st.text_input('Enter Gemini API token:', type='password')
        if api_key:
            st.session_state.api_key = api_key
        else:
            st.warning('Please enter your Gemini API token!', icon='⚠️')
    else:
        st.success('Using API key from .env file ✅')

    # Configure the Gemini model
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.0-flash", generation_config=generation_config)
        except Exception as e:
            st.error(f"Error with the API key: {e}", icon="🚨")


    with st.container():
        l, m, r = st.columns((1, 3, 1))
        with l: st.empty()
        with m: st.empty()
        with r: st.empty()

    options = option_menu(
        "Dashboard", 
        ["Home", "About Us", "Chat", "PDF Reader"],
        icons=['book', 'globe', 'chat', 'file-pdf'],
        menu_icon="book", 
        default_index=0,
        styles={
            "icon": {"color": "#dec960", "font-size": "20px"},
            "nav-link": {"font-size": "17px", "text-align": "left", "margin": "5px", "--hover-color": "#262730"},
            "nav-link-selected": {"background-color": "#262730"}          
        })
    

if 'message' not in st.session_state:
    st.session_state.message = []

if 'chat_session' not in st.session_state:
    st.session_state.chat_session = None

# Options : Home
if options == "Home" :

   st.title("Welcome to Knetsu's Love Chatbot 💖")
   st.subheader("Love and Relationship Guidance at Your Fingertips")
   st.write("Hello! I'm Knetsu, your AI-powered love chatbot. Whether you're looking for advice on relationships, need help navigating your feelings, or just want to chat about love, I'm here for you!")
    
   st.write("This chatbot is designed to help you navigate your feelings, answer love-related questions, and offer relationship advice.")
    
   st.markdown("""
    ### What you can ask me:
    - 💌 How do I confess to my crush?
    - 💔 How can I move on from heartbreak?
    - ❤️ What are signs someone likes me?
    
    _Go to the **Love Chat** tab to get started!_
    """)
  
elif options == "About Us" :
    st.title("💘 About Us")
    
    st.markdown("""
    Welcome to **Knetsu's Love Chatbot**! 💖  
    We're here to bring comfort, clarity, and caring advice to anyone navigating the world of **love and relationships**.

    ### 🌟 Our Mission
    To offer a safe and supportive space where users can ask love-related questions — whether you're:
    - Crushing on someone,
    - Going through heartbreak,
    - In a relationship and need guidance,
    - Or just curious about matters of the heart.

    ### 🤖 How It Works
    Knetsu is powered by AI and designed to respond like a caring friend with helpful, thoughtful answers.  
    Every message is focused on helping you understand your feelings and support your emotional well-being.

    ### 👤 About the Creator
    This chatbot was created by **Knet**, a BSIT student with a passion for technology and helping others.  
    Built using **Streamlit**, **Google Gemini AI**, and 💡 a whole lot of heart!

    ---
    _Thanks for visiting. We hope Knetsu can brighten your day!_ 💗
    """)

elif options == "PDF Reader":
    st.title("PDF Knowledge Assistant")
    
    # PDF upload
    uploaded_file = st.file_uploader("Upload a PDF document", type="pdf")
    
    if uploaded_file is not None:
        # Process the PDF
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        # Extract text and create chunks
        with st.spinner("Processing PDF..."):
            text = extract_text_from_pdf(tmp_file_path)
            chunks = create_chunks(text)
            st.session_state.chroma_db.add_documents(chunks)
            st.success("PDF processed!")
        
        # Query interface
        query = st.text_input("Ask a question about the PDF:")
        if query:
            with st.spinner("Finding detailed answer..."):
                # Get relevant chunks with more context
                relevant_chunks = st.session_state.chroma_db.search(query, n_results=3)
                
                # Prepare detailed prompt
                context = "\n\nContext Section " + "\nContext Section ".join([f"{i+1}: {chunk}" for i, chunk in enumerate(relevant_chunks)])
                
                prompt = f"""Based on the provided context sections from the PDF document, please provide a detailed and comprehensive answer to the question. 
                If you find relevant information in multiple context sections, synthesize them together.
                If the answer cannot be fully derived from the context, please indicate what information is missing.
                
                Context:
                {context}
                
                Question: {query}
                
                Please provide a detailed answer, explaining your reasoning and citing specific parts of the context when relevant:"""
                
                # Get response from Gemini
                response = model.generate_content(prompt)
                
                # Display response in a nice format
                st.markdown("### Answer:")
                st.markdown(response.text)
                
                # Show sources
                with st.expander("View source sections from the document"):
                    for i, chunk in enumerate(relevant_chunks):
                        st.markdown(f"**Section {i+1}:**")
                        st.markdown(chunk)
                        st.markdown("---")

elif options == 'Chat':
        # Avatar selection (only once)
    avatar_choice = st.selectbox(
        "Choose your love advisor 💞",
        options=["Knetsu (Female)", "Knetsu (Male)"],
        index=0
    )

    # Assign avatar based on selection
    user_avatar = "./user_avatar.png"  # Adjust paths as needed
    if avatar_choice == "Knetsu (Female)":
        bot_avatar = "./knetsu_f.png"  # Adjust paths as needed
    else:
        bot_avatar = "./knetsu_m.png"

    # Now use bot_avatar in your chat display code:
    for message in st.session_state.messages:
        if message["role"] == "system":
            continue
        avatar = user_avatar if message["role"] == "user" else bot_avatar
        try:
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])
        except Exception:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])


    # Initialize chat session and messages ONCE
    if "chat_session" not in st.session_state or st.session_state.chat_session is None:
        st.session_state.chat_session = model.start_chat(history=[])
        st.session_state.messages = []

        # Initial assistant message introducing itself
        response = st.session_state.chat_session.send_message(
            "You will act and introduce yourself as the following : " + SYSTEM_PROMPT
        )
        reply = response.text.strip()
        st.session_state.messages.append({"role": "assistant", "content": reply})

    # Chat avatars
    bot_avatar = "knetsu_m.png"  # your assistant avatar image
    user_avatar = "user_avatar.png"  # your user avatar image

    # Show chat history
    for message in st.session_state.messages:
        if message["role"] == "system":
            continue

        avatar = user_avatar if message["role"] == "user" else bot_avatar

        # With this updated version using the correct Exception class
        try:
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])
        except Exception:
            # fallback in case avatar path is invalid
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Input field for new messages
    if user_message := st.chat_input("Ask me anything about love... 💌"):
        st.session_state.messages.append({"role": "user", "content": user_message})

        with st.chat_message("user", avatar=user_avatar):
            st.markdown(user_message)

        response = st.session_state.chat_session.send_message(
            f"Remember, you are a love advice expert only. Answer this as a love-related question: {user_message}"
        )
        reply = response.text.strip()

        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant", avatar=bot_avatar):
            st.markdown(reply)


