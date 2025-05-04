import streamlit as st
from PIL import Image
import torch
import torchvision.transforms as transforms
import numpy as np
import PyPDF2
import io
import json
from datetime import datetime
import os
from pathlib import Path
import zipfile
# Set page config
st.set_page_config(
    page_title="Multimodal Chat Interface",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #f7f7f8;
    }
    .assistant-message {
        background-color: #ffffff;
    }
    .chat-input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 1rem;
        background-color: white;
        border-top: 1px solid #e5e7eb;
        z-index: 100;
    }
    .chat-container {
        margin-bottom: 5rem;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
    }
    .file-upload-area {
        border: 2px dashed #e5e7eb;
        border-radius: 0.5rem;
        padding: 1rem;
        text-align: center;
        margin-top: 0.5rem;
        cursor: pointer;
    }
    .file-upload-area:hover {
        border-color: #2563eb;
    }
    .preview-container {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 0.5rem;
    }
    .preview-item {
        position: relative;
        width: 100px;
        height: 100px;
        border-radius: 0.5rem;
        overflow: hidden;
    }
    .preview-item img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    .message-content {
        line-height: 1.5;
        font-size: 1rem;
    }
    .message-time {
        font-size: 0.75rem;
        color: #666;
        margin-top: 0.5rem;
    }
    .file-preview {
        margin-top: 1rem;
        padding: 0.5rem;
        background-color: #f8f9fa;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_files' not in st.session_state:
    st.session_state.current_files = []
if 'message_id' not in st.session_state:
    st.session_state.message_id = 0
if 'input_key' not in st.session_state:
    st.session_state.input_key = 0

# Function to process uploaded files
def process_uploaded_files(files):
    images = []
    pdf_texts = []
    pdf_files = []
    
    for file in files:
        if file.type.startswith('image/'):
            image = Image.open(file)
            images.append(image)
        elif file.type == 'application/pdf':
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
            pdf_text = ""
            for page in pdf_reader.pages:
                pdf_text += page.extract_text()
            pdf_texts.append(pdf_text)
            pdf_files.append(file)
    
    return images, pdf_texts, pdf_files

# Function to create a message object
def create_message(role, content, images=None, pdf_texts=None, pdf_files=None):
    message = {
        "id": st.session_state.message_id,
        "role": role,
        "content": content,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    if images:
        message["images"] = images
    if pdf_texts:
        message["pdf_texts"] = pdf_texts
    if pdf_files:
        message["pdf_files"] = pdf_files
    
    return message

# Model processing functions
class MultimodalModel:
    def _init_(self):
        # Initialize your model here
        pass
    
    def process_inputs(self, text_input, images, pdf_texts):
        """
        Process multiple inputs and generate appropriate responses
        """
        # Initialize response components
        response_text = ""
        response_images = []
        response_pdf_texts = []
        
        # Process text input
        if text_input:
            response_text += f"Processed text: {text_input}\n"
        
        # Process images
        if images:
            response_text += f"Processed {len(images)} images\n"
            # Here you would process images with your model
            # For demo, we'll just return the input images
            response_images = images
        
        # Process PDFs
        if pdf_texts:
            response_text += f"Processed {len(pdf_texts)} PDFs\n"
            # Here you would process PDFs with your model
            # For demo, we'll just return the input PDF texts
            response_pdf_texts = pdf_texts
        
        # Combine all responses
        if not response_text:
            response_text = "No input provided"
        
        return response_text, response_images, response_pdf_texts

# Initialize model
model = MultimodalModel()

# Main chat interface
st.title("🤖 Multimodal Chat")

# Chat container
chat_container = st.container()
with chat_container:
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            # Message content
            st.markdown(f'<div class="message-content">{message["content"]}</div>', unsafe_allow_html=True)
            
            # Display images if present
            if "images" in message and message["images"]:
                st.markdown('<div class="file-preview">', unsafe_allow_html=True)
                st.write("Attached Images:")
                for img in message["images"]:
                    st.image(img, use_column_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Display PDF content if present
           # Display PDF content if present
            if "pdf_texts" in message and message["pdf_texts"]:
                st.markdown('<div class="file-preview">', unsafe_allow_html=True)
                st.write("Extracted PDF Text:")
                for i, pdf_text in enumerate(message["pdf_texts"]):
                    with st.expander(f"📄 PDF {i+1}"):
                        st.markdown(
                            f"""
                            <div style='max-height: 200px; overflow-y: auto; background-color: #f0f0f0; padding: 10px; border-radius: 5px;'>
                                <pre>{pdf_text}</pre>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
                st.markdown('</div>', unsafe_allow_html=True)


# Chat input container
with st.container():
    st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
    
    # File upload area
    uploaded_files = st.file_uploader(
        "Upload files",
        type=["png", "jpg", "jpeg", "pdf"],
        accept_multiple_files=True,
        key=f"file_uploader_{st.session_state.input_key}",
        help="Upload images or PDFs to discuss with the model"
    )
    
    # Update current files in session state
    if uploaded_files:
        st.session_state.current_files = uploaded_files
    
    # Display file previews
    if st.session_state.current_files:
        st.markdown('<div class="preview-container">', unsafe_allow_html=True)
        for i, file in enumerate(st.session_state.current_files):
            if file.type.startswith('image/'):
                image = Image.open(file)
                st.image(image, width=100)
            elif file.type == 'application/pdf':
                st.markdown(f'<div class="preview-item">📄 {file.name}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Text input
    text_input = st.chat_input("Message Multimodal Chat...", key=f"chat_input_{st.session_state.input_key}")

# Process new message only when chat input is submitted
if text_input is not None:  # Only process when chat input is submitted
    # Process uploaded files
    images, pdf_texts, pdf_files = process_uploaded_files(st.session_state.current_files)
    
    # Create user message
    user_message = create_message(
        "user",
        text_input if text_input else "I've shared some files to discuss",
        images=images,
        pdf_texts=pdf_texts,
        pdf_files=pdf_files
    )
    
    # Add user message to chat history
    st.session_state.chat_history.append(user_message)
    st.session_state.message_id += 1
    
    # Generate model response
    with st.spinner("Processing inputs..."):
        try:
            # Process all inputs through the model
            response_text, response_images, response_pdf_texts = model.process_inputs(
                text_input,
                images,
                pdf_texts
            )
            
            # Create model response
            model_response = create_message(
                "assistant",
                response_text,
                images=response_images,
                pdf_texts=response_pdf_texts
            )
            
            # Add model response to chat history
            st.session_state.chat_history.append(model_response)
            st.session_state.message_id += 1
            
            # Clear current files and increment input key
            st.session_state.current_files = []
            st.session_state.input_key += 1
            
            # Force a rerun to update the display
            st.rerun()
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Clear chat button
if st.button("🗑 Clear Chat", type="secondary"):
    st.session_state.chat_history = []
    st.session_state.current_files = []
    st.session_state.message_id = 0
    st.session_state.input_key += 1


# Footer
st.markdown("---")
st.markdown("Made with ❤ using Streamlit")


# poppler_path = r"C:\poppler\poppler-24.08.0\Library\bin"