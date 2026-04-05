# configuration and settings
import os
from dotenv import load_dotenv

load_dotenv(".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not GEMINI_API_KEY:
    raise EnvironmentError("GEMINI_API_KEY is not set. Check your .env file.")
if not TAVILY_API_KEY:
    print("Warning: TAVILY_API_KEY is not set. Web search will be disabled.")

QUESTIONS = [
    "Where do you want to go and when?",
    "How long is your trip (in days)?",
    "What's your total budget (excluding flights)?",
    "What's your passport nationality?",
    "What are your travel interests? (Select multiple or add your own!)",
]