import os
import httpx
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from loguru import logger

class SearchInterface:
    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        self.google_cse_id = os.getenv("GOOGLE_CSE_ID")
        self.bing_api_key = os.getenv("BING_SEARCH_API_KEY")

    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        results = []
        if self.google_api_key and self.google_cse_id:
            results = await self._search_google(query, limit)
        
        if not results and self.bing_api_key:
            results = await self._search_bing(query, limit)
        
        # Fallback to a mock or a simple scraper if no keys provided (for demo/dev)
        if not results:
            logger.warning(f"No Search API keys found. Returning mock results for query: {query}")
            results = [
                {"title": f"Example Business for {query}", "link": "https://example.com", "snippet": "A sample business snippet."}
            ]
            
        return results

    async def _search_google(self, query: str, limit: int) -> List[Dict[str, Any]]:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.google_api_key,
            "cx": self.google_cse_id,
            "q": query,
            "num": limit
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                return [{"title": i["title"], "link": i["link"], "snippet": i["snippet"]} for i in data.get("items", [])]
            except Exception as e:
                logger.error(f"Google search failed: {e}")
                return []

    async def _search_bing(self, query: str, limit: int) -> List[Dict[str, Any]]:
        url = "https://api.bing.microsoft.com/v7.0/search"
        headers = {"Ocp-Apim-Subscription-Key": self.bing_api_key}
        params = {"q": query, "count": limit}
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                return [{"title": i["name"], "link": i["url"], "snippet": i["snippet"]} for i in data.get("webPages", {}).get("value", [])]
            except Exception as e:
                logger.error(f"Bing search failed: {e}")
                return []

search_client = SearchInterface()

async def scrape_page(url: str) -> str:
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            return soup.get_text(separator=' ', strip=True)[:2000] # Limit content
    except Exception as e:
        logger.error(f"Scraping failed for {url}: {e}")
        return ""
