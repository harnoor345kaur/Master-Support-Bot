import os
from dotenv import load_dotenv
from google import genai

from llm.base import BaseLLM

load_dotenv()


class GeminiLLM(BaseLLM):
    def __init__(self, model_name: str = "models/gemini-flash-latest"):
        api_key = os.getenv("API_KEY")
        if not api_key:
            raise ValueError("API_KEY not found in environment variables.")

        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        prompt = f"""SYSTEM:
{system_prompt}

USER:
{user_prompt}
"""

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )

        return response.text.strip()
