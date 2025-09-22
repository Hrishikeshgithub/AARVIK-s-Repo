# Save as test_gemini_models.py
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GOOGLE_AI_API_KEY")

try:
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=api_key)
    models = llm.client.list_models()
    print("Available models:")
    for model in models:
        print(model.name)
except Exception as e:
    print(f"Error: {str(e)}")