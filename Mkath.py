import streamlit as st
import google.generativeai as genai

gemini_api_key = st.secrets['gemini_key']



# Main chat interface
st.title("  Genie :female_genie:")
st.caption("!!:ghost:  HAKUNA MATATA :ghost:!!")

# Initialize message history
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

# Display chat messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Chat input
if prompt := st.chat_input():
    if not gemini_api_key:
        st.info("Please add your Gemini API key to continue.")
        st.stop()

    # Configure Gemini
genai.configure(api_key=gemini_api_key)
generation_config = {
  "temperature": 0.4,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="tunedModels/mergeddatajsonl-g7atpb6m5g1p",
  generation_config=generation_config,
)
   
   

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Get Gemini response
    try:
        response = model.generate_content(prompt)
        msg = response.text

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.chat_message("assistant").write(msg)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
