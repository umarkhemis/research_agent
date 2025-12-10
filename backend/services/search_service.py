
import requests
import arxiv
from typing import List, Dict, Optional
import config
from utils.error_handler import logger, handle_errors, APIError, ErrorContext
from agents.cache_manager import cache
from utils.deduplicator import deduplicator


class SearchAgent:
    """Handles paper search with robust error handling across multiple databases"""
    
    def __init__(self):
        # Semantic Scholar
        self.semantic_scholar_url = "https://api.semanticscholar.org/graph/v1/paper/search"
        self.headers = {}
        
        # Add API key if available (increases rate limits)
        if config.SEMANTIC_SCHOLAR_API_KEY:
            self.headers["x-api-key"] = config.SEMANTIC_SCHOLAR_API_KEY
        
        # ArXiv client
        self.arxiv_client = arxiv.Client()
        
        logger.info("Search Agent initialized (Semantic Scholar + ArXiv)")
    
    @handle_errors#(default_return=[])
    def search_papers(
        self, 
        query: str, 
        limit: int = config.DEFAULT_PAPER_LIMIT,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        open_access_only: bool = False,
        databases: List[str] = None
    ) -> List[Dict]:
        """
        Search for papers across multiple databases
        
        Args:
            query: Search query
            limit: Maximum number of results
            year_from: Filter papers from this year onwards
            year_to: Filter papers up to this year
            open_access_only: Only return open access papers
            databases: List of databases to search ['semantic_scholar', 'arxiv']
                      If None, searches all available databases
            
        Returns:
            List of paper dictionaries (deduplicated)
        """
        # Default to all databases
        if databases is None:
            databases = ['semantic_scholar', 'arxiv']
        
        # Check cache first (for combined search)
        cache_key = f"{query}_{limit}_{databases}"
        cached_results = cache.get_topic_cache(cache_key, limit)
        if cached_results:
            logger.info(f"Returning cached results for: {query}")
            return cached_results
        
        all_papers = []
        
        # Search Semantic Scholar
        if 'semantic_scholar' in databases:
            try:
                ss_papers = self._search_semantic_scholar(
                    query, limit, year_from, year_to, open_access_only
                )
                all_papers.extend(ss_papers)
                logger.info(f"Semantic Scholar: {len(ss_papers)} papers")
            except Exception as e:
                logger.warning(f"Semantic Scholar search failed: {str(e)}")
        
        # Search ArXiv
        if 'arxiv' in databases:
            try:
                arxiv_papers = self._search_arxiv(
                    query, limit, year_from, year_to
                )
                all_papers.extend(arxiv_papers)
                logger.info(f"ArXiv: {len(arxiv_papers)} papers")
            except Exception as e:
                logger.warning(f"ArXiv search failed: {str(e)}")
        
        # Deduplicate papers
        unique_papers, duplicates = deduplicator.deduplicate(all_papers)
        
        logger.info(f"Total: {len(unique_papers)} unique papers ({len(duplicates)} duplicates removed)")
        
        # Limit results
        if len(unique_papers) > limit:
            unique_papers = unique_papers[:limit]
        
        # Cache the results
        cache.set_topic_cache(cache_key, unique_papers, limit)
        
        return unique_papers
    
    def _search_semantic_scholar(
        self,
        query: str,
        limit: int,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        open_access_only: bool = False
    ) -> List[Dict]:
        """Search Semantic Scholar API"""
        
        # Validate limit
        if limit > config.MAX_PAPER_LIMIT:
            logger.warning(f"Limit {limit} exceeds max, using {config.MAX_PAPER_LIMIT}")
            limit = config.MAX_PAPER_LIMIT
        
        params = {
            "query": query,
            "limit": limit,
            "fields": "title,abstract,year,url,openAccessPdf,authors,citationCount,venue,publicationDate,externalIds"
        }
        
        # Add optional filters
        if year_from:
            params["year"] = f"{year_from}-"
        if year_to:
            if "year" in params:
                params["year"] = f"{year_from}-{year_to}"
            else:
                params["year"] = f"-{year_to}"
        
        if open_access_only:
            params["openAccessPdf"] = ""
        
        with ErrorContext(f"Searching Semantic Scholar for: '{query}'"):
            try:
                response = requests.get(
                    self.semantic_scholar_url, 
                    params=params, 
                    headers=self.headers,
                    timeout=30
                )
                response.raise_for_status()
                
                data = response.json()
                papers = data.get("data", [])
                
                if not papers:
                    logger.warning(f"No papers found in Semantic Scholar for: {query}")
                    return []
                
                # Process and clean paper data
                cleaned_papers = []
                for paper in papers:
                    cleaned_paper = self._clean_paper_data(paper, source='semantic_scholar')
                    if cleaned_paper:
                        cleaned_papers.append(cleaned_paper)
                
                return cleaned_papers
                
            except requests.exceptions.Timeout:
                logger.error("Semantic Scholar request timed out")
                raise APIError("Search request timed out. Please try again.")
            
            except requests.exceptions.RequestException as e:
                logger.error(f"Semantic Scholar API request failed: {str(e)}")
                raise APIError(f"Failed to search papers: {str(e)}")
            
            except Exception as e:
                logger.error(f"Unexpected error during Semantic Scholar search: {str(e)}")
                raise APIError(f"Unexpected error: {str(e)}")
    
    def _search_arxiv(
        self,
        query: str,
        limit: int,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None
    ) -> List[Dict]:
        """Search ArXiv API"""
        with ErrorContext(f"Searching ArXiv for: '{query}'"):
            try:
                # Build ArXiv search
                search = arxiv.Search(
                    query=query,
                    max_results=limit,
                    sort_by=arxiv.SortCriterion.Relevance
                )
                
                papers = []
                for result in self.arxiv_client.results(search):
                    # Filter by year if specified
                    paper_year = result.published.year
                    if year_from and paper_year < year_from:
                        continue
                    if year_to and paper_year > year_to:
                        continue
                    
                    # Convert to standard format
                    paper = self._clean_arxiv_paper(result)
                    papers.append(paper)
                
                return papers
                
            except Exception as e:
                logger.error(f"ArXiv search failed: {str(e)}")
                raise APIError(f"ArXiv search error: {str(e)}")
    
    def _clean_arxiv_paper(self, result) -> Dict:
        """Clean and format ArXiv paper"""
        try:
            # Extract DOI if available
            doi = result.doi if hasattr(result, 'doi') and result.doi else None

            # Extract arXiv ID
            arxiv_id = result.entry_id.split('/abs/')[-1] if result.entry_id else None

            # Safely get title and abstract
            title = result.title.strip() if result.title else "Untitled"
            abstract = result.summary.strip() if result.summary else "No abstract available"

            paper = {
                "title": title,
                "abstract": abstract,
                "year": result.published.year if result.published else "Unknown",
                "url": result.entry_id or "",
                "authors": [author.name for author in result.authors if author.name],
                "citation_count": 0,
                "venue": f"arXiv preprint {result.primary_category}" if hasattr(result, 'primary_category') else "arXiv",
                "publication_date": result.published.strftime("%Y-%m-%d") if result.published else "Unknown",
                "has_pdf": True,
                "pdf_url": result.pdf_url if hasattr(result, 'pdf_url') else None,
                "paper_id": result.entry_id or title,
                "source": "arxiv",
                "arxiv_id": arxiv_id,
                "doi": doi
            }

            return paper

        except Exception as e:
            logger.warning(f"Error cleaning ArXiv paper: {str(e)}")
            return None
    
    
    
    def _clean_paper_data(self, paper: Dict, source: str = 'semantic_scholar') -> Optional[Dict]:
        """
        Clean and validate paper data
        """
        try:
            # Required fields
            if not paper.get("title"):
                logger.debug("Skipping paper without title")
                return None

            # Extract author names safely
            authors = paper.get("authors", [])
            author_names = [a.get("name", "Unknown") for a in authors if a.get("name")]

            # Safely get abstract
            abstract = paper.get("abstract")
            if abstract and isinstance(abstract, str):
                abstract = abstract.strip()
            else:
                abstract = "No abstract available"

            # Safely get title
            title = paper.get("title", "Untitled")
            if isinstance(title, str):
                title = title.strip()

            # Build cleaned paper object
            cleaned = {
                "title": title,
                "abstract": abstract,
                "year": paper.get("year") or "Unknown",
                "url": paper.get("url", ""),
                "authors": author_names,
                "citation_count": paper.get("citationCount", 0),
                "venue": paper.get("venue") or "Unknown",
                "publication_date": paper.get("publicationDate") or "Unknown",
                "has_pdf": False,
                "pdf_url": None,
                "source": source
            }

            # Check for PDF availability
            pdf_info = paper.get("openAccessPdf")
            if pdf_info and isinstance(pdf_info, dict):
                pdf_url = pdf_info.get("url")
                if pdf_url:
                    cleaned["has_pdf"] = True
                    cleaned["pdf_url"] = pdf_url

            # Generate unique ID for caching
            cleaned["paper_id"] = cleaned["url"] or cleaned["title"]

            return cleaned

        except Exception as e:
            logger.warning(f"Error cleaning paper data: {str(e)}")
            return None
    
    
    
    
    
    
    
    def get_paper_by_id(self, paper_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific paper
        
        Args:
            paper_id: Semantic Scholar paper ID
            
        Returns:
            Paper details or None
        """
        url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}"
        params = {
            "fields": "title,abstract,year,url,openAccessPdf,authors,citationCount,references,citations"
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=15)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch paper {paper_id}: {str(e)}")
            return None


# Global search agent instance
search_agent = SearchAgent()


