import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import logging
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Page configuration and styling
def setup_page():
    """Configure page settings and layout"""
    st.set_page_config(
        page_title="Genie - Medical Assistant",
        page_icon="🧞‍♀️",
        layout="wide"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .stTitle {
        color: #6739b7;
    }
    .chat-container {
        padding: 20px;
        border-radius: 10px;
        background-color: #f9f9f9;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize Gemini API
def initialize_gemini() -> Optional[genai.GenerativeModel]:
    """Initialize and configure Gemini API"""
    try:
        # Get API key from secrets
        gemini_api_key = st.secrets.get('gemini_key')
        
        if not gemini_api_key:
            st.error("Gemini API key is missing. Please add it to your Streamlit secrets.")
            return None
            
        # Configure Gemini
        genai.configure(api_key=gemini_api_key)
        
        # Generation configuration
        generation_config = {
            "temperature": 0.4,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }
        
        # Safety settings - keeping moderate safety levels while allowing medical content
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }
        
        # Initialize model
        model = genai.GenerativeModel(
            model_name="tunedModels/mergeddatajsonl-g7atpb6m5g1p",
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        logging.info("Gemini API initialized successfully")
        return model
        
    except Exception as e:
        logging.error(f"Error initializing Gemini API: {str(e)}")
        st.error(f"Failed to initialize AI model: {str(e)}")
        return None

# Generate response using Gemini
def generate_response(model: genai.GenerativeModel, prompt: str) -> str:
    """Generate AI response using the Gemini model"""
    try:
        # Craft a detailed prompt for medical context
        system_prompt = """
        You are a knowledgeable medical professional specializing in pathology.
        Provide accurate, evidence-based information on medical questions.
        For diagnoses, always clarify that this is information only and the user should consult their doctor.
        When discussing medical conditions:
        1. Explain in clear, concise language
        2. Provide relevant scientific context when helpful
        3. Mention standard approaches to diagnosis or treatment when appropriate
        4. Be honest when something is outside your knowledge scope
        """
        
        # Combine system prompt with user query
        full_prompt = f"{system_prompt}\n\nUser question: {prompt}"
        
        # Generate response
        response = model.generate_content(full_prompt)
        return response.text
        
    except Exception as e:
        logging.error(f"Error generating response: {str(e)}")
        return f"I apologize, but I encountered an error while processing your request: {str(e)}"

# Display chat history
def display_chat_history(messages: List[Dict[str, str]]):
    """Display the chat conversation history"""
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# Main application function
def main():
    """Main application entry point"""
    # Setup page
    setup_page()
    
    # Application header
    st.title("🧞‍♀️ Genie - Medical Assistant")
    st.caption("Your trusted companion for medical information")
    
    # Initialize model
    model = initialize_gemini()
    
    if not model:
        st.warning("Application is running in limited mode due to configuration issues.")
        st.stop()
    
    # Initialize session state for message history
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant", "content": "Hello! I'm Genie, your medical information assistant. How can I help you today?"}
        ]
    
    # Display chat container
    with st.container(border=True):
        # Display chat history
        display_chat_history(st.session_state.messages)
        
        # Get user input
        prompt = st.chat_input("Ask me about medical conditions, pathology, or health concerns...")
        
        if prompt:
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display the new user message
            with st.chat_message("user"):
                st.write(prompt)
            
            # Show typing indicator
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    # Generate and display assistant response
                    response = generate_response(model, prompt)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.write(response)
    
    # Add helpful information footer
    st.divider()
    st.caption("**Note:** This assistant provides information only and is not a substitute for professional medical advice, diagnosis, or treatment.")

# Application entry point
if __name__ == "__main__":
    main()
