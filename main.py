import streamlit as st
import PyPDF2 
import io
import requests
from dotenv import load_dotenv 
import os
load_dotenv()
st.set_page_config(page_title="AI Resume Critiquer",page_icon="📃",layout="centered") 
st.title("AI Resume Critiquer")
st.markdown("Upload your resume and get AI-powered feedback tailored to your needs!")  
LLAMA_API_URL = os.getenv("api_url")

uploaded_file=st.file_uploader("Upload your resume (PFD or TXT)",type=["pdf","txt"])
job_role=st.text_input("Enter the job role you'retargetting (optional)")
analyse=st.button("Analyse Resume")  
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    return uploaded_file.read().decode("utf-8")
def query_ollama_llama3(prompt):
    try:
        response = requests.post(
            LLAMA_API_URL,
            json={
                "model": "llama3.2",
                "prompt": prompt,
                "stream": False
            }
        )
        response.raise_for_status()
        return response.json()["response"]
    except Exception as e:
        return f"Error communicating with Ollama: {str(e)}"
if analyse and uploaded_file:
    try:
        file_content=extract_text_from_file(uploaded_file)
        if not file_content.strip():
            st.error("File does not have any content")
            st.stop() 
        prompt = f"""Please analyze this resume and provide constructive feedback. 
        Focus on the following aspects:
        1. Content clarity and impact
        2. Skills presentation
        3. Experience descriptions
        4. Specific improvements for {job_role if job_role else 'general job applications'} 
         Resume content:
        {file_content}
        
        Please provide your analysis in a clear, structured format with specific recommendations."""
        st.markdown("### Analysis Results")
        result = query_ollama_llama3(prompt)
        st.markdown(result)
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")