import httpx
import asyncio
import re
from config import settings
from core.exceptions import LLMUnavailableError, LLMTimeoutError
from core.logging import get_logger

logger = get_logger(__name__)

class OpenRouterClient:
    def __init__(self):
        self.base_url = settings.openrouter_base_url
        self.model = settings.openrouter_model
        self.api_key = settings.openrouter_api_key
        self.timeout = settings.llm_timeout

    async def generate(self, prompt: str, system: str = "") -> str:
        if not self.api_key:
            raise LLMUnavailableError("OpenRouter API key is not configured.")

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://campusos.app", # Optional but recommended by OpenRouter
            "X-Title": "Campus OS Local Server", # Optional
        }
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(3):
                try:
                    response = await client.post(url, json=payload, headers=headers)
                    response.raise_for_status()
                    data = response.json()
                    
                    choices = data.get("choices", [])
                    if not choices:
                        raise ValueError("No choices returned from OpenRouter API")
                        
                    response_text = choices[0].get("message", {}).get("content", "")
                    
                    # Strip markdown code fences
                    code_fence_pattern = re.compile(r"^```(?:json|txt|md)?\s*(.*?)\s*```$", re.DOTALL | re.MULTILINE)
                    match = code_fence_pattern.search(response_text)
                    if match:
                        response_text = match.group(1).strip()
                    
                    return response_text

                except httpx.ConnectError as e:
                    logger.error(f"Failed to connect to OpenRouter on {self.base_url}")
                    raise LLMUnavailableError("Could not connect to OpenRouter server.") from e
                
                except httpx.ReadTimeout as e:
                    logger.error("OpenRouter request timed out.")
                    raise LLMTimeoutError("OpenRouter inference timed out.") from e
                
                except httpx.HTTPStatusError as e:
                    if e.response.status_code >= 500 and attempt < 2:
                        logger.warning(f"OpenRouter returned 5xx, retrying {attempt+1}/2...")
                        await asyncio.sleep(1)
                        continue
                    else:
                        logger.error(f"OpenRouter returned HTTP error: {e.response.status_code} - {e.response.text}")
                        raise LLMUnavailableError(f"OpenRouter error: {e.response.status_code}") from e
                
                except Exception as e:
                    logger.error(f"Unexpected error communicating with OpenRouter: {e}")
                    raise LLMUnavailableError(f"Unexpected error: {e}") from e
            
            raise LLMUnavailableError("OpenRouter failed after retries.")

    async def is_available(self) -> bool:
        if not self.api_key:
            return False
            
        url = f"{self.base_url}/auth/key"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url, headers=headers)
                return response.status_code == 200
        except Exception:
            return False

# Global instance
llm_client = OpenRouterClient()
