import google.generativeai as genai
from PIL import Image
import streamlit as st
import time

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

def analyze_image(image_input, retries=3):
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    if isinstance(image_input, str):
        image = Image.open(image_input)
    else:
        image = Image.open(image_input)

    prompt = """
    You are an expert telecom site audit engineer inspect infrastructure (Tower, DG, Rectifier, Batteries, Grounding, Cabinets).
    Analyze the image and list all observed physical anomalies, safety hazards, and compliance issues.
    
    Output concise bullet points describing specific technical faults.
    If no defects are visible, respond with: "No issue observed".
    """

    for attempt in range(retries):
        try:
            response = model.generate_content([prompt, image])
            return response.text
        except Exception as e:
            if attempt == retries - 1:
                st.error(f"Vision API Error: {str(e)}")
                return "Technician did not capture close-up image"
            time.sleep(2 ** attempt)
