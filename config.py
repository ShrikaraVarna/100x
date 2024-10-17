import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    SESSION_TYPE = 'filesystem'
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
    FALLBACK_MESSAGE = "I cannot answer the query using the information from the file."
