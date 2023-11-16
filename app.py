import streamlit as st
from llama_index import VectorStoreIndex, ServiceContext, Document
from llama_index.llms import OpenAI
import openai
from llama_index import SimpleDirectoryReader
from dataclasses import dataclass
import pypdf
import os
from typing import Literal
import streamlit.components.v1 as components
import time


openai.api_key = ""



# Set custom theme colors
st.set_page_config(
    page_title="Med Assist",
    page_icon="🧬",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items=None
)
st.title("Chat with Med Assist 💬🩺")
# Load data using llamaindex
@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading."):
        reader = SimpleDirectoryReader(input_dir="./Data", recursive=True)
        docs = reader.load_data()
        service_context = ServiceContext.from_defaults(
            llm=OpenAI(
                model="gpt-3.5-turbo",
                temperature=0.2,
                system_prompt = (
                    "You have the medical report of a patient."
                    "Assume all input prompts to be related to the medical data. "
                    "Answer queries regarding patient medical report. "
                    "Provide insights into diagnoses and suggest potential courses of action."
                )

            )
        )
        index = VectorStoreIndex.from_documents(docs, service_context=service_context)
        return index

uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"])
if uploaded_file:
        # Save the uploaded file to the same location
        file_path = os.path.join("./Data", uploaded_file.name)
        with open(file_path, "wb") as file:
            file.write(uploaded_file.getbuffer())

index = load_data()
import re

class Conversation:
    def _init_(self):
        # Your initialization logic here
        self.memory = {}  # Replace with actual memory setup
        self.year = None

    def setup(self):
        # Your setup logic here
        pass

    def update_year(self, year):
        self.year = year

def initialize_conversation():
    # Your code to set up and return the conversation object
    conversation = Conversation()
    conversation.setup()
    return conversation

# Initialize chat engine
chat_engine = index.as_chat_engine(verbose=True)
# Initialize chat messages history and other attributes
if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {"role": "assistant", "content": "I can help you with your Medical Report 🧬"}
    ]
    st.session_state.history = []  # Initialize history attribute
    st.session_state.token_count = 0  # Initialize token_count attribute
    if "conversation" not in st.session_state.keys() or st.session_state.conversation is None:
        st.session_state.conversation = initialize_conversation()


# Apply styles to the prompt using st.markdown
chat_form_style = """
    <style>
        body {
            background-image: url('your_image_url.jpg'); /* Replace 'your_image_url.jpg' with your image URL */
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }

        .stForm {
            background-color: rgba(255, 255, 255, 0.8); /* Set a background color with opacity */
            padding: 20px;
            border-radius: 10px;
        }
    </style>
"""
st.markdown(chat_form_style, unsafe_allow_html=True)

response = None  # Initialize response variable

with st.form("chat-form"):
    prompt = st.text_input(
        'Ask me a question about your Medical Report 🩺',
        key="human_prompt",
    )
    if st.form_submit_button("Submit", type="primary"):
        start_time = time.time()
        # Generate response if needed
        with st.spinner("Thinking..."):
            response = chat_engine.chat(prompt)
            st.write(response.response)

            st.write("Time taken with cache:", time.time() - start_time)

            # Append user prompt to history
            user_message = {"role": "user", "content": prompt}
            st.session_state.messages.append(user_message)

            # Append assistant message to history
            assistant_message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(assistant_message)

# # Area chart based on user input
# if response:
#     response_text = response.response
#     st.write("Chatbot Response:", response_text)  # Debugging statement

#     data_from_chatbot = [int(x) for x in response_text.split() if x.isdigit()]
#     st.write("Extracted data from chatbot:", data_from_chatbot)  # Debugging statement

#     st.area_chart(data_from_chatbot)

# Display chat history
for message in reversed(st.session_state.messages):
    with st.container():
        st.image("user.png" if message["role"] == "user" else "chatbot.png", width=50)
        st.write(message["content"])


st.write(" ")
