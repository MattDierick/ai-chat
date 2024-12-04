import os
import streamlit as st
import requests
from dataclasses import dataclass
from PIL import Image

# Define your constants
USER = "user"
ASSISTANT = "ai"
MESSAGES = "messages"
#API_URL = "https://aigw.xc.edgecnf.com/ollama"  # Replace with your actual API endpoint
API_URL = os.getenv("AIGW_API_URL")
AI_MODEL = os.getenv("AI_MODEL")
AI_TEMP = float(os.getenv("AI_TEMP", 0.7))

# JSON template for API request
json_template = {
    "model": f"{AI_MODEL}",
    "messages": [],
    "temperature": AI_TEMP
}

# Load avatar images from local files
USER_AVATAR = Image.open("./user.png")  # Replace with the actual path to the user avatar image
ASSISTANT_AVATAR = Image.open("./ai.png")  # Replace with the actual path to the assistant avatar image

st.set_page_config(page_title='AIGW Simply Chat', page_icon=None, layout="centered", initial_sidebar_state="auto", menu_items=None)

hide_streamlit_style = """
                <style>
                div[data-testid="stToolbar"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stDecoration"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stStatusWidget"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                #MainMenu {
                visibility: hidden;
                height: 0%;
                }
                header {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                footer {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                </style>
                """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

@dataclass
class Message:
    role: str
    content: str

# Initialize session state messages
if MESSAGES not in st.session_state:
    st.session_state[MESSAGES] = [Message(role=ASSISTANT, content="Welcome to Corporate AI Services. Services are governed under Corporate AI Governance. Use it responsibly. How can I help?")]

# Display existing messages
for msg in st.session_state[MESSAGES]:
    avatar = ASSISTANT_AVATAR if msg.role == ASSISTANT else USER_AVATAR
    st.chat_message(msg.role, avatar=avatar).write(msg.content)

# Take user input
#prompt = st.text_input("Enter a prompt here:", key="input_field")
prompt = st.text_area("Enter a prompt here:", key="input_field", max_chars=100, height=100)

# If user submits input
if st.button("Submit"):
    if prompt:
        # Update messages list in JSON template with user input
        json_template["messages"].append({
            "role": USER,
            "content": prompt
        })
        
        # Append user message to session state
        st.session_state[MESSAGES].append(Message(role=USER, content=prompt))
        st.chat_message(USER, avatar=USER_AVATAR).write(prompt)


        # Add spinner while waiting for response
        with st.spinner("Waiting for response..."):
            try:
                # Send POST request to API endpoint with updated JSON template
                response = requests.post(API_URL, json=json_template)
                
                # Display response from API
                if response.status_code == 200:
                    response_data = response.json()

                    model_name = response_data.get("model", "Unknown Model")  # Default to "Unknown Model" if key is missing
                    
                    # Extract and display assistant's response from choices
                    if "choices" in response_data:
                        for choice in response_data["choices"]:
                            if "message" in choice and "content" in choice["message"]:
                                assistant_response = choice["message"]["content"]
                                st.session_state[MESSAGES].append(Message(role=ASSISTANT, content=assistant_response))
                                st.chat_message(ASSISTANT, avatar=ASSISTANT_AVATAR).write(assistant_response)
                                st.markdown(f"<div style='text-align: right; font-style: italic; font-size: 12px;'>LLM Model Used: {model_name}</div>", unsafe_allow_html=True)
                            else:
                                st.warning("Invalid format in API response: 'message' or 'content' not found.")
                    else:
                        st.warning("Invalid format in API response: 'choices' not found.")
                        
                else:
                    #st.error(f"Failed to get response from API. Status code: {response.status_code}")
                    st.error(f"Unfortunately, I don't quite like your question. Please try again. My mood: {response.status_code}")
            except requests.exceptions.RequestException as e:
                st.error(f"Error sending request: {e}")

