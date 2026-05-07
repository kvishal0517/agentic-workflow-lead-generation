import os
import json
from typing import Optional, Any, Dict
import httpx
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

class LLMInterface:
    def __init__(self):
        self.use_groq = os.getenv("USE_GROQ", "false").lower() == "true"
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    async def call(self, prompt: str, system_prompt: str = "You are a helpful assistant.", json_mode: bool = False) -> str:
        if self.use_groq and self.groq_api_key:
            return await self._call_groq(prompt, system_prompt, json_mode)
        else:
            return await self._call_ollama(prompt, system_prompt, json_mode)

    async def _call_ollama(self, prompt: str, system_prompt: str, json_mode: bool) -> str:
        url = f"{self.ollama_base_url}/api/generate"
        payload = {
            "model": self.ollama_model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
            }
        }
        if json_mode:
            payload["format"] = "json"

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("response", "")
            except Exception as e:
                logger.error(f"Ollama call failed: {e}")
                raise

    async def _call_groq(self, prompt: str, system_prompt: str, json_mode: bool) -> str:
        # Placeholder for Groq implementation using httpx or groq SDK
        # For simplicity, using a generic OpenAI-compatible interface if needed
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        payload = {
            "model": "llama-3.1-70b-versatile",
            "messages": messages,
            "temperature": 0.1,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except Exception as e:
                logger.error(f"Groq call failed: {e}")
                # Fallback to Ollama if Groq fails?
                return await self._call_ollama(prompt, system_prompt, json_mode)

llm = LLMInterface()
