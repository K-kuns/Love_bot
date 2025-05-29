import streamlit as st

# Initialize state if not already done
if "user_profile" not in st.session_state:
    st.session_state.user_profile = "default_user.png"

# Sidebar or somewhere to update user profile
user_type = st.selectbox("Choose your character", ["Girl", "Boy"])
if user_type == "Girl":
    st.session_state.user_profile = "girl_profile.png"
else:
    st.session_state.user_profile = "boy_profile.png"

# Chat interface
st.image(st.session_state.user_profile, width=50)  # Show user icon

user_input = st.text_input("You:", key="chat_input")

if user_input:
    # Immediately show user icon with the message
    st.image(st.session_state.user_profile, width=50)
    st.write(f"You: {user_input}")
    # Handle chatbot reply below...
