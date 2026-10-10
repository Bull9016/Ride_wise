import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    """
    Wrapper for the NeoStats OpenAI deployment.
    Handles tool calling and robust error catching.
    """
    def __init__(self):
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "Neo-Hackathon")
        
        if not self.endpoint or not self.api_key:
            raise ValueError("AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY must be set in .env")

        self.client = OpenAI(
            base_url=self.endpoint,
            api_key=self.api_key
        )

    def generate_response(self, messages: list, tools: list = None) -> dict:
        """
        Calls the LLM with the conversation history and available tools.
        """
        try:
            kwargs = {
                "model": self.deployment_name,
                "messages": messages,
                "temperature": 0.0, # Zero temperature for strict factual accuracy
            }
            
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"
                
            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message
            
        except Exception as e:
            raise RuntimeError(f"LLM API Error: {str(e)}")
