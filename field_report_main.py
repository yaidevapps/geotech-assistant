import streamlit as st
from PIL import Image
import google.generativeai as genai
from geotech_helper import GeotechEngineerAssistant

# Page configuration
st.set_page_config(
    page_title="Geotechnical Engineer Assistant",
    page_icon="🌍",
    layout="wide"
)

# Initialize session state
if 'chat' not in st.session_state:
    st.session_state.chat = None
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'image_analyzed' not in st.session_state:
    st.session_state.image_analyzed = False
if 'current_image' not in st.session_state:
    st.session_state.current_image = None

# Sidebar for API key
with st.sidebar:
    st.title("Settings")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    if api_key:
        assistant = GeotechEngineerAssistant(api_key)
    else:
        assistant = GeotechEngineerAssistant()
    
    # Add clear chat button
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.session_state.chat = assistant.start_chat()
        st.session_state.image_analyzed = False
        st.rerun()

# Main title
st.title("🌍 Geotechnical Engineer Assistant")
st.markdown("""
This AI assistant helps analyze geotechnical site conditions, soil characteristics, and provides preliminary engineering recommendations. 
Upload site images for analysis and engage in technical discussions about soil engineering considerations.
""")

# Initialize chat if not already done
if st.session_state.chat is None:
    st.session_state.chat = assistant.start_chat()

# File uploader
uploaded_file = st.file_uploader("Upload a site image for geotechnical analysis", type=['png', 'jpg', 'jpeg'])

# Main interface
if uploaded_file:
    # Display image
    image = Image.open(uploaded_file)
    st.image(image, caption="Geotechnical Site Image", use_container_width=True)
    
    # Analyze button
    if not st.session_state.image_analyzed:
        if st.button("Analyze Site Conditions", type="primary"):
            with st.spinner("Analyzing geotechnical conditions..."):
                # Store image for reference
                st.session_state.current_image = image
                
                # Get initial analysis
                report = assistant.analyze_image(image, st.session_state.chat)
                
                # Add the report to chat history
                st.session_state.messages.append({"role": "assistant", "content": report})
                st.session_state.image_analyzed = True
                st.rerun()

# Display chat history
st.markdown("### 💬 Geotechnical Analysis Discussion")
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if st.session_state.image_analyzed:
    if prompt := st.chat_input("Ask technical questions about the site conditions..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                response = assistant.send_message(st.session_state.chat, prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

# Footer with instructions
st.markdown("---")
st.markdown("""
### How to Use This Geotechnical Assistant
1. Upload a site image showing soil conditions, geological features, or excavations
2. Click "Analyze Site Conditions" for an initial geotechnical assessment
3. Ask specific technical questions about:
   - Soil classification and characteristics
   - Foundation recommendations
   - Geological hazards
   - Site investigation requirements
   - Environmental considerations
4. Download the analysis report for documentation

Example technical questions:
- What additional soil testing would you recommend based on the visible conditions?
- Can you elaborate on the potential foundation challenges for this site?
- What are the key environmental protection considerations for this location?
- What geologic hazards should we be particularly concerned about?
- What soil improvement methods would you suggest based on the visible conditions?
""")

# Download button for chat history
if st.session_state.messages:
    chat_history = "\n\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in st.session_state.messages])
    st.download_button(
        "Download Geotechnical Analysis",
        chat_history,
        file_name="geotechnical_analysis_report.txt",
        mime="text/plain"
    )