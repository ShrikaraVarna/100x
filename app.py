import os
import streamlit as st
from services.ai_services import call_openai_api, call_claude_api
from services.json_utils import load_json, generate_prompt, is_query_answerable, summarize_json

# Function to handle JSON file uploads and processing
def process_upload(file):
    if file is not None and file.name.endswith('.json'):
        try:
            file_path = os.path.join('uploads', file.name)
            os.makedirs('uploads', exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())

            json_data = load_json(file_path)
            summary = summarize_json(json_data, file.name)

            return json_data, summary
        except Exception as e:
            st.error(f'Error processing file: {str(e)}')
            return None, None
    else:
        st.error('Invalid file type. Please upload a JSON file.')
        return None, None

# Streamlit application layout
st.title("JSON Query Application")

# File upload section
uploaded_file = st.file_uploader("Upload JSON file", type="json")

if uploaded_file:
    json_data, summary = process_upload(uploaded_file)
    
    if json_data and summary:
        st.success('File successfully uploaded and processed.')

        user_query = st.text_input("Enter your query:")
        api_choice = st.selectbox("Choose API:", ["openai", "claude"])

        if st.button("Submit Query"):
            if user_query:
                prompt = generate_prompt(summary, user_query)
                try:
                    if api_choice == 'openai':
                        answer = call_openai_api(prompt)
                    elif api_choice == 'claude':
                        answer = call_claude_api(prompt)
                    else:
                        st.error('Invalid API choice.')
                        answer = None
                    
                    if answer:
                        st.write("Response:")
                        st.write(answer)
                    else:
                        st.warning("No response from API.")
                except Exception as e:
                    st.error(f'Error communicating with AI API: {str(e)}')
            else:
                st.error('Please enter a query.')
