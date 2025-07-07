import os
try:
    from dotenv import load_dotenv
    import google.genai as genai
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
except ImportError:
    client = None  # Or raise if needed only in runtime

def get_client():
    return client
