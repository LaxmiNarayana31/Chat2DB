import os 
from dotenv import load_dotenv
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI

load_dotenv(verbose = True)

# Custom LLM class for generate response 
class LlmHelper():
    def googleGeminiLlm():
        gemini_model = os.getenv("MODEL_NAME")
        gemini_api_key = os.getenv("GOOGLE_API_KEY")
        llm = ChatGoogleGenerativeAI(
            model = gemini_model, 
            google_api_key = gemini_api_key,
            temperature = 0.7, top_p = 0.85
        )
        return llm
    
