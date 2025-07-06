"""
Web Search Tool - SerpAPI wrapper for web search functionality
"""

import os
import requests
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class WebSearchTool:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SERPAPI_KEY")
        self.base_url = "https://serpapi.com/search"
        self.default_params = {
            "engine": "google",
            "num": 10,
            "hl": "en",
            "gl": "us"
        }
    
    def search(self, query: str, num_results: int = 10, **kwargs) -> Dict[str, Any]:
        """
        Perform web search using SerpAPI
        
        Args:
            query: Search query string
            num_results: Number of results to return
            **kwargs: Additional search parameters
            
        Returns:
            Dict containing search results and metadata
        """
        if not self.api_key:
            return self._error_response("SerpAPI key not found. Please set SERPAPI_KEY environment variable.")
        
        try:
            params = {
                **self.default_params,
                "q": query,
                "num": num_results,
                "api_key": self.api_key,
                **kwargs
            }
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return self._process_results(data, query)
            
        except requests.exceptions.RequestException as e:
            return self._error_response(f"Request failed: {str(e)}")
        except Exception as e:
            return self._error_response(f"Unexpected error: {str(e)}")
    
    def search_news(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """Search for news articles"""
        return self.search(query, num_results, tbm="nws")
    
    def search_images(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """Search for images"""
        return self.search(query, num_results, tbm="isch")
    
    def _process_results(self, data: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Process and format search results"""
        organic_results = data.get("organic_results", [])
        news_results = data.get("news_results", [])
        
        processed_results = []
        
        # Process organic results
        for result in organic_results:
            processed_results.append({
                "title": result.get("title", ""),
                "link": result.get("link", ""),
                "snippet": result.get("snippet", ""),
                "source": "web",
                "date": result.get("date", ""),
                "position": result.get("position", 0)
            })
        
        # Process news results
        for result in news_results:
            processed_results.append({
                "title": result.get("title", ""),
                "link": result.get("link", ""),
                "snippet": result.get("snippet", ""),
                "source": "news",
                "date": result.get("date", ""),
                "position": result.get("position", 0)
            })
        
        return {
            "success": True,
            "query": query,
            "results": processed_results,
            "total_results": len(processed_results),
            "search_metadata": data.get("search_metadata", {}),
            "tool": "web_search"
        }
    
    def _error_response(self, error_message: str) -> Dict[str, Any]:
        """Return standardized error response"""
        return {
            "success": False,
            "error": error_message,
            "results": [],
            "total_results": 0,
            "tool": "web_search"
        }
    
    def validate_api_key(self) -> bool:
        """Validate if API key is working"""
        if not self.api_key:
            return False
        
        try:
            test_params = {
                "engine": "google",
                "q": "test",
                "api_key": self.api_key,
                "num": 1
            }
            
            response = requests.get(self.base_url, params=test_params, timeout=10)
            return response.status_code == 200
            
        except Exception:
            return False
    
    def get_search_suggestions(self, query: str) -> List[str]:
        """Get search suggestions for a query"""
        # TODO: Implement search suggestions using SerpAPI
        # For now, return basic suggestions
        return [
            f"{query} definition",
            f"{query} examples",
            f"{query} benefits",
            f"{query} challenges",
            f"latest {query} news"
        ] 