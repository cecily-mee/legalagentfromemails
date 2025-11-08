from langchain_google_genai.google_api_imports import genai
import os
from dotenv import load_dotenv

# Load the .env file to get your API key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("Error: GOOGLE_API_KEY not found in .env file.")
else:
    genai.configure(api_key=api_key)
    print("Listing all available models for your API key...")
    print("="*30)
    
    try:
        for model in genai.list_models():
            # We are looking for models that can be used for 'generateContent'
            if 'generateContent' in model.supported_generation_methods:
                print(f"Model name: {model.name}")
                print("   Supported methods: {model.supported_generation_methods}\n")
    
    except Exception as e:
        print(f"An error occurred: {e}")
        print("\nPlease double-check that your GOOGLE_API_KEY is correct in the .env file.")

    print("="*30)
    print("Find a multimodal model in the list above (like 'gemini-pro-vision') and paste its 'Model name' into src/agents.py")