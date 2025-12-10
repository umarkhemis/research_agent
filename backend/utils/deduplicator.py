

from typing import List, Dict, Tuple
from fuzzywuzzy import fuzz
from utils.error_handler import logger


class Deduplicator:
    """Deduplicate papers using fuzzy matching and DOI"""
    
    def __init__(self, title_threshold: int = 90, author_threshold: int = 85):
        """
        Initialize deduplicator
        
        Args:
            title_threshold: Minimum fuzzy match score for titles (0-100)
            author_threshold: Minimum fuzzy match score for authors (0-100)
        """
        self.title_threshold = title_threshold
        self.author_threshold = author_threshold
        logger.info(f"Deduplicator initialized (title_threshold={title_threshold})")
    
    
    def deduplicate(self, papers: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Deduplicate a list of papers
        
        Args:
            papers: List of paper dictionaries
            
        Returns:
            Tuple of (unique_papers, duplicates)
        """
        if not papers:
            return [], []
        
        unique_papers = []
        duplicates = []
        seen_dois = set()
        seen_arxiv_ids = set()
        
        for paper in papers:
            # Check DOI first (exact match) - FIXED
            doi = paper.get('doi') or ''
            doi = doi.strip().lower() if doi else ''
            if doi and doi in seen_dois:
                duplicates.append(paper)
                logger.debug(f"Duplicate found (DOI): {paper.get('title', '')[:50]}")
                continue
            
            # Check arXiv ID (exact match) - FIXED
            arxiv_id = paper.get('arxiv_id') or ''
            arxiv_id = arxiv_id.strip().lower() if arxiv_id else ''
            if arxiv_id and arxiv_id in seen_arxiv_ids:
                duplicates.append(paper)
                logger.debug(f"Duplicate found (arXiv): {paper.get('title', '')[:50]}")
                continue
            
            # Fuzzy matching on title and authors
            is_duplicate = False
            for unique_paper in unique_papers:
                if self._is_duplicate(paper, unique_paper):
                    duplicates.append(paper)
                    is_duplicate = True
                    logger.debug(f"Duplicate found (fuzzy): {paper.get('title', '')[:50]}")
                    break
            
            if not is_duplicate:
                unique_papers.append(paper)
                if doi:
                    seen_dois.add(doi)
                if arxiv_id:
                    seen_arxiv_ids.add(arxiv_id)
        
        logger.info(f"Deduplication: {len(papers)} → {len(unique_papers)} unique, {len(duplicates)} duplicates")
        return unique_papers, duplicates

    
    def _is_duplicate(self, paper1: Dict, paper2: Dict) -> bool:
        """
        Check if two papers are duplicates using fuzzy matching
        
        Args:
            paper1: First paper
            paper2: Second paper
            
        Returns:
            True if papers are duplicates
        """
        # Compare titles
        title1 = self._normalize_string(paper1.get('title', ''))
        title2 = self._normalize_string(paper2.get('title', ''))
        
        if not title1 or not title2:
            return False
        
        title_score = fuzz.ratio(title1, title2)
        
        # If titles match closely, it's likely a duplicate
        if title_score >= self.title_threshold:
            # Double-check with authors if available
            authors1 = self._normalize_authors(paper1.get('authors', []))
            authors2 = self._normalize_authors(paper2.get('authors', []))
            
            if authors1 and authors2:
                author_score = fuzz.ratio(authors1, authors2)
                if author_score >= self.author_threshold:
                    return True
            else:
                # If no authors available, rely on title alone
                return True
        
        return False
    
    def _normalize_string(self, text: str) -> str:
        """Normalize string for comparison"""
        if not text:
            return ""
        
        # Convert to lowercase and remove extra whitespace
        text = text.lower().strip()
        text = ' '.join(text.split())
        
        # Remove common punctuation
        for char in ['.', ',', ':', ';', '!', '?', '"', "'", '(', ')', '[', ']']:
            text = text.replace(char, '')
        
        return text
    
    def _normalize_authors(self, authors: List[str]) -> str:
        """Normalize author list to a single string"""
        if not authors:
            return ""
        
        # Take first 3 authors, normalize names
        normalized = []
        for author in authors[:3]:
            # Remove extra whitespace and convert to lowercase
            author = ' '.join(author.lower().split())
            normalized.append(author)
        
        return ' '.join(normalized)
    
    def merge_paper_data(self, papers: List[Dict], prefer_source: str = None) -> Dict:
        """
        Merge data from duplicate papers, preferring more complete information
        
        Args:
            papers: List of duplicate papers
            prefer_source: Preferred data source ('semantic_scholar', 'arxiv', etc.)
            
        Returns:
            Merged paper dictionary
        """
        if not papers:
            return {}
        
        if len(papers) == 1:
            return papers[0]
        
        # Start with preferred source or first paper
        if prefer_source:
            merged = next((p for p in papers if p.get('source') == prefer_source), papers[0])
        else:
            merged = papers[0].copy()
        
        # Merge fields, preferring non-empty values
        for paper in papers[1:]:
            for key, value in paper.items():
                # Skip if current value is good
                if merged.get(key) and value:
                    # Special handling for certain fields
                    if key == 'citation_count':
                        # Take highest citation count
                        merged[key] = max(merged.get(key, 0), value)
                    elif key == 'authors' and len(value) > len(merged.get(key, [])):
                        # Take longer author list
                        merged[key] = value
                    elif not merged.get(key):
                        # Fill in missing values
                        merged[key] = value
        
        # Mark as merged from multiple sources
        sources = list(set(p.get('source', 'unknown') for p in papers))
        merged['sources'] = sources
        merged['merged_from_count'] = len(papers)
        
        return merged


# Global deduplicator instance
deduplicator = Deduplicator()