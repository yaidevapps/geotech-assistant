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
Chat directly about geotechnical topics or upload site images for detailed analysis.
""")

# Initialize chat if not already done
if st.session_state.chat is None:
    st.session_state.chat = assistant.start_chat()

# Create tabs for different functionalities
tab1, tab2 = st.tabs(["💬 Chat", "📷 Image Analysis"])

with tab1:
    st.markdown("### General Geotechnical Discussion")
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask any geotechnical engineering questions..."):
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

with tab2:
    st.markdown("### Site Image Analysis")
    # File uploader
    uploaded_file = st.file_uploader("Upload a site image for geotechnical analysis", type=['png', 'jpg', 'jpeg'])

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

# Footer with instructions
st.markdown("---")
st.markdown("""
### How to Use This Geotechnical Assistant
1. Chat directly about geotechnical topics in the Chat tab
2. For site-specific analysis:
   - Switch to the Image Analysis tab
   - Upload a site image showing soil conditions, geological features, or excavations
   - Click "Analyze Site Conditions" for an initial assessment
3. Continue the discussion about either general topics or the analyzed image

Example questions:
- What are the typical foundation types for clay soils?
- How do you determine the bearing capacity of sandy soils?
- What factors influence soil liquefaction potential?
- What are the best practices for slope stability analysis?
- How do you assess soil consolidation characteristics?
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