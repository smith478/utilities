import requests
import os
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import time

class WebSearcher:
    def __init__(self, search_api_key=None):
        self.search_api_key = search_api_key or os.environ.get("SEARCH_API_KEY")
        self.last_request_time = 0
        self.min_request_interval = 1  # seconds between requests
    
    def search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Search the web for information about the query."""
        # This is a placeholder. In a real implementation, you would use:
        # - SerpAPI (https://serpapi.com/)
        # - Google Custom Search API
        # - Bing Search API
        # - DuckDuckGo API
        
        # Implement your preferred search API here
        # Example with a hypothetical search API:
        try:
            # Rate limiting
            self._respect_rate_limit()
            
            # Make the search request
            response = requests.get(
                "https://api.example.com/search",
                params={
                    "q": query,
                    "num": num_results,
                    "api_key": self.search_api_key
                }
            )
            
            if response.status_code != 200:
                return []
                
            data = response.json()
            results = []
            
            # Process the results
            for item in data.get("results", [])[:num_results]:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", "")
                })
                
            return results
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def fetch_content(self, url: str) -> str:
        """Fetch and extract the main content from a URL."""
        try:
            self._respect_rate_limit()
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                return ""
                
            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Remove unwanted elements
            for element in soup(["script", "style", "header", "footer", "nav"]):
                element.decompose()
                
            # Extract text
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = "\n".join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            print(f"Error fetching content from {url}: {e}")
            return ""
    
    def _respect_rate_limit(self):
        """Ensure we don't exceed rate limits for APIs and websites."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            time.sleep(sleep_time)
            
        self.last_request_time = time.time()