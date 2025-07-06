"""
Academic Search Tool - ArXiv and PubMed API wrappers for academic research
"""

import os
import requests
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from urllib.parse import urlencode

# Load environment variables
load_dotenv()

class AcademicSearchTool:
    def __init__(self, pubmed_api_key: Optional[str] = None):
        self.pubmed_api_key = pubmed_api_key or os.getenv("PUBMED_API_KEY")
        self.arxiv_base_url = "http://export.arxiv.org/api/query"
        self.pubmed_base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    def search_arxiv(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Search ArXiv for academic papers
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            Dict containing search results and metadata
        """
        try:
            params = {
                "search_query": query,
                "start": 0,
                "max_results": max_results,
                "sortBy": "relevance",
                "sortOrder": "descending"
            }
            
            url = f"{self.arxiv_base_url}?{urlencode(params)}"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            return self._process_arxiv_results(response.text, query)
            
        except requests.exceptions.RequestException as e:
            return self._error_response(f"ArXiv request failed: {str(e)}")
        except Exception as e:
            return self._error_response(f"ArXiv search error: {str(e)}")
    
    def search_pubmed(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Search PubMed for medical/biological papers
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            Dict containing search results and metadata
        """
        try:
            # Step 1: Search for paper IDs
            search_params = {
                "db": "pubmed",
                "term": query,
                "retmax": max_results,
                "retmode": "xml"
            }
            
            if self.pubmed_api_key:
                search_params["api_key"] = self.pubmed_api_key
            
            search_url = f"{self.pubmed_base_url}/esearch.fcgi"
            search_response = requests.get(search_url, params=search_params, timeout=30)
            search_response.raise_for_status()
            
            # Extract paper IDs
            paper_ids = self._extract_pubmed_ids(search_response.text)
            
            if not paper_ids:
                return {
                    "success": True,
                    "query": query,
                    "results": [],
                    "total_results": 0,
                    "tool": "pubmed_search"
                }
            
            # Step 2: Fetch paper details
            return self._fetch_pubmed_details(paper_ids, query)
            
        except requests.exceptions.RequestException as e:
            return self._error_response(f"PubMed request failed: {str(e)}")
        except Exception as e:
            return self._error_response(f"PubMed search error: {str(e)}")
    
    def search_combined(self, query: str, max_results_per_source: int = 5) -> Dict[str, Any]:
        """
        Search both ArXiv and PubMed and combine results
        
        Args:
            query: Search query string
            max_results_per_source: Max results from each source
            
        Returns:
            Dict containing combined search results
        """
        arxiv_results = self.search_arxiv(query, max_results_per_source)
        pubmed_results = self.search_pubmed(query, max_results_per_source)
        
        combined_results = []
        
        if arxiv_results.get("success"):
            combined_results.extend(arxiv_results.get("results", []))
        
        if pubmed_results.get("success"):
            combined_results.extend(pubmed_results.get("results", []))
        
        return {
            "success": True,
            "query": query,
            "results": combined_results,
            "total_results": len(combined_results),
            "sources": ["arxiv", "pubmed"],
            "tool": "academic_search"
        }
    
    def _process_arxiv_results(self, xml_content: str, query: str) -> Dict[str, Any]:
        """Process ArXiv XML response"""
        try:
            root = ET.fromstring(xml_content)
            namespace = {"atom": "http://www.w3.org/2005/Atom"}
            
            entries = root.findall("atom:entry", namespace)
            results = []
            
            for entry in entries:
                title = entry.find("atom:title", namespace)
                summary = entry.find("atom:summary", namespace)
                published = entry.find("atom:published", namespace)
                link = entry.find("atom:id", namespace)
                
                authors = []
                for author in entry.findall("atom:author", namespace):
                    name = author.find("atom:name", namespace)
                    if name is not None:
                        authors.append(name.text)
                
                results.append({
                    "title": title.text if title is not None else "",
                    "abstract": summary.text if summary is not None else "",
                    "authors": authors,
                    "published_date": published.text if published is not None else "",
                    "link": link.text if link is not None else "",
                    "source": "arxiv",
                    "type": "preprint"
                })
            
            return {
                "success": True,
                "query": query,
                "results": results,
                "total_results": len(results),
                "tool": "arxiv_search"
            }
            
        except ET.ParseError as e:
            return self._error_response(f"ArXiv XML parsing error: {str(e)}")
    
    def _extract_pubmed_ids(self, xml_content: str) -> List[str]:
        """Extract PubMed IDs from search response"""
        try:
            root = ET.fromstring(xml_content)
            ids = []
            
            for id_elem in root.findall(".//Id"):
                if id_elem.text:
                    ids.append(id_elem.text)
            
            return ids
            
        except ET.ParseError:
            return []
    
    def _fetch_pubmed_details(self, paper_ids: List[str], query: str) -> Dict[str, Any]:
        """Fetch detailed information for PubMed papers"""
        try:
            ids_str = ",".join(paper_ids)
            
            fetch_params = {
                "db": "pubmed",
                "id": ids_str,
                "retmode": "xml"
            }
            
            if self.pubmed_api_key:
                fetch_params["api_key"] = self.pubmed_api_key
            
            fetch_url = f"{self.pubmed_base_url}/efetch.fcgi"
            fetch_response = requests.get(fetch_url, params=fetch_params, timeout=30)
            fetch_response.raise_for_status()
            
            return self._process_pubmed_results(fetch_response.text, query)
            
        except requests.exceptions.RequestException as e:
            return self._error_response(f"PubMed fetch failed: {str(e)}")
    
    def _process_pubmed_results(self, xml_content: str, query: str) -> Dict[str, Any]:
        """Process PubMed XML response"""
        try:
            root = ET.fromstring(xml_content)
            results = []
            
            for article in root.findall(".//PubmedArticle"):
                # Extract title
                title_elem = article.find(".//ArticleTitle")
                title = title_elem.text if title_elem is not None else ""
                
                # Extract abstract
                abstract_elem = article.find(".//AbstractText")
                abstract = abstract_elem.text if abstract_elem is not None else ""
                
                # Extract authors
                authors = []
                for author in article.findall(".//Author"):
                    last_name = author.find("LastName")
                    first_name = author.find("ForeName")
                    if last_name is not None and first_name is not None:
                        authors.append(f"{first_name.text} {last_name.text}")
                
                # Extract publication date
                pub_date = article.find(".//PubDate")
                date_str = ""
                if pub_date is not None:
                    year = pub_date.find("Year")
                    month = pub_date.find("Month")
                    if year is not None:
                        date_str = year.text
                        if month is not None:
                            date_str += f"-{month.text}"
                
                # Extract PMID
                pmid = article.find(".//PMID")
                pmid_text = pmid.text if pmid is not None else ""
                
                results.append({
                    "title": title,
                    "abstract": abstract,
                    "authors": authors,
                    "published_date": date_str,
                    "pmid": pmid_text,
                    "link": f"https://pubmed.ncbi.nlm.nih.gov/{pmid_text}/" if pmid_text else "",
                    "source": "pubmed",
                    "type": "peer_reviewed"
                })
            
            return {
                "success": True,
                "query": query,
                "results": results,
                "total_results": len(results),
                "tool": "pubmed_search"
            }
            
        except ET.ParseError as e:
            return self._error_response(f"PubMed XML parsing error: {str(e)}")
    
    def _error_response(self, error_message: str) -> Dict[str, Any]:
        """Return standardized error response"""
        return {
            "success": False,
            "error": error_message,
            "results": [],
            "total_results": 0,
            "tool": "academic_search"
        } 