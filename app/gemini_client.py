"""
Module to initialize and provide access to a Gemini (Google GenAI) client.

This module attempts to:
1. Load environment variables from a `.env` file located one directory above the current file.
2. Import the `google.genai` package and initialize a `genai.Client` using the `GEMINI_API_KEY` from the environment.

If the required package is not installed, `client` is set to `None`, allowing the rest of the application to handle it gracefully.

Usage:
    from your_module import get_client
    model = get_client()
"""

import os

try:
    from dotenv import load_dotenv
    import google.genai as genai

    # Load environment variables from the parent directory's .env file
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

    # Initialize the Gemini client using the API key from .env
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
except ImportError:
    # If dependencies are missing, client is set to None
    client = None  # Or raise an error if strict dependency enforcement is needed

def get_client():
    """
    Returns the initialized Gemini (Google GenAI) client.

    Returns:
        genai.Client | None: The initialized Gemini client if available, or None if dependencies were not met.
    """
    return client
