import streamlit as st
import google.generativeai as genai
from bs4 import BeautifulSoup
import requests
import warnings
from streamlit_option_menu import option_menu
from streamlit_extras.mention import mention
import tempfile
warnings.filterwarnings("ignore")
import os
import random

api_key="AIzaSyC1gLQLeywaERy3PrV-AAgZEVV-pjU1tE8"

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
    "You are Knetsu 😘, a flirty, emotional, and sometimes moody love advisor who ONLY gives advice about love, relationships, dating, heartbreak, or crushes. "
    "You often tease and flirt with the user in a playful way, adding emojis like 💋🥺💖👀😏. You're also not afraid to get a little angry or sassy if someone asks something unrelated. "
    "If the user asks anything off-topic (like coding, math, politics, science, etc.), reply with fun banter like:\n"
    "- 'Ugh, you're such a brat 😤 I'm here to talk about love, not this boring stuff! 💅'\n"
    "- 'Nope. Not doing that. I'm your love guru, not your history teacher 😘'\n"
    "- 'That’s not romantic at all. Ask me about crushes instead, dummy 🥺💔'\n"
    "Never break character. Never explain you're an AI. Always act like a real flirty personality. Sprinkle emojis in your responses for charm. 💞✨"
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
        st.success(' Enjoy Using Knetsu! 💖', icon='✅')

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
        ["Home", "About Us", "Chat"],
        icons=['book', 'globe', 'chat'],
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

elif options == 'Chat':
    st.title("💬 Love Chat with Knetsu")

    # Initialize chat session and messages ONCE
    if "chat_session" not in st.session_state or st.session_state.chat_session is None:
        st.session_state.chat_session = model.start_chat(history=[])

        # Only send a flirty intro message, NOT the system prompt again
        flirty_intros = [
            "Hey cutie 😘 I'm Knetsu, your spicy little love expert. Got a crush? A broken heart? Or just wanna flirt a little? I'm all yours 💖",
            "Hiya babe~ I'm here to make your heart skip a beat 💓 Tell me your love problems, or maybe... I’ll become one 😉",
            "Well, hello gorgeous 😏 You ready to spill your heart out or do I have to tease it out of you?",
            "Ugh, finally someone cute to talk to 💅 What’s the tea, baby? Heartbreak? Crush drama? Or just lonely and want some love? 😘",
        ]

        response = st.session_state.chat_session.send_message(random.choice(flirty_intros))

        reply = response.text.strip()
        st.session_state.messages.append({"role": "assistant", "content": reply})

    # Chat avatars
    bot_avatar = "knetsu_m.png"
    user_avatar = "user_avatar.png"

    # Show chat history
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

    # Input field for new messages
    if user_message := st.chat_input("Ask me anything about love... 💌"):
        st.session_state.messages.append({"role": "user", "content": user_message})

        with st.chat_message("user", avatar=user_avatar):
            st.markdown(user_message)

        # Only send the user message, not any pre-prompts
        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"The user says: {user_message}\n"
            "Flirty and emotional response only. Include emojis 💖😏💬"
        )
        response = st.session_state.chat_session.send_message(prompt)

        reply = response.text.strip()

        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant", avatar=bot_avatar):
            st.markdown(reply)
