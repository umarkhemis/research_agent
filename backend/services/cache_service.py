

import pickle
import os
from pathlib import Path
from typing import Any, Optional, List, Dict
from datetime import datetime, timedelta
import config
from utils.error_handler import logger


class CacheManager:
    """Manages caching for API responses and LLM outputs"""
    
    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Separate cache directories for different types
        self.topic_cache_dir = self.cache_dir / "topics"
        self.paper_cache_dir = self.cache_dir / "papers"
        
        self.topic_cache_dir.mkdir(exist_ok=True)
        self.paper_cache_dir.mkdir(exist_ok=True)
        
        self.enabled = config.ENABLE_CACHE
        logger.info(f"Cache Manager initialized (enabled: {self.enabled})")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        if not self.enabled:
            return None
        
        try:
            # Determine cache directory based on key prefix
            if key.startswith("search_") or key.startswith("topic_"):
                cache_file = self.topic_cache_dir / f"{key}.pkl"
            else:
                cache_file = self.paper_cache_dir / f"{key}.pkl"
            
            if not cache_file.exists():
                return None
            
            # Check if cache is expired
            file_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if file_age > timedelta(hours=config.CACHE_EXPIRY_DAYS * 24):
                logger.debug(f"Cache expired for key: {key}")
                cache_file.unlink()  # Delete expired cache
                return None
            
            # Load cached data
            with open(cache_file, 'rb') as f:
                data = pickle.load(f)
            
            logger.debug(f"Cache hit: {key}")
            return data
            
        except Exception as e:
            logger.warning(f"Cache retrieval failed for {key}: {str(e)}")
            return None
    
    def set(self, key: str, value: Any) -> bool:
        """
        Store value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            # Determine cache directory based on key prefix
            if key.startswith("search_") or key.startswith("topic_"):
                cache_file = self.topic_cache_dir / f"{key}.pkl"
            else:
                cache_file = self.paper_cache_dir / f"{key}.pkl"
            
            # Save to cache
            with open(cache_file, 'wb') as f:
                pickle.dump(value, f)
            
            logger.debug(f"Cache set: {key}")
            return True
            
        except Exception as e:
            logger.warning(f"Cache storage failed for {key}: {str(e)}")
            return False
    
    def clear(self, cache_type: Optional[str] = None) -> int:
        """
        Clear cache
        
        Args:
            cache_type: 'topics', 'papers', or None for all
            
        Returns:
            Number of files deleted
        """
        deleted = 0
        
        try:
            if cache_type == "topics" or cache_type is None:
                for file in self.topic_cache_dir.glob("*.pkl"):
                    file.unlink()
                    deleted += 1
            
            if cache_type == "papers" or cache_type is None:
                for file in self.paper_cache_dir.glob("*.pkl"):
                    file.unlink()
                    deleted += 1
            
            logger.info(f"Cleared {deleted} cache files (type: {cache_type or 'all'})")
            return deleted
            
        except Exception as e:
            logger.error(f"Cache clearing failed: {str(e)}")
            return deleted
    
    def get_cache_stats(self) -> dict:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache stats
        """
        try:
            topic_files = list(self.topic_cache_dir.glob("*.pkl"))
            paper_files = list(self.paper_cache_dir.glob("*.pkl"))
            
            topic_size = sum(f.stat().st_size for f in topic_files)
            paper_size = sum(f.stat().st_size for f in paper_files)
            
            stats = {
                "enabled": self.enabled,
                "topic_cache_files": len(topic_files),
                "paper_cache_files": len(paper_files),
                "total_files": len(topic_files) + len(paper_files),
                "topic_cache_size_mb": round(topic_size / (1024 * 1024), 2),
                "paper_cache_size_mb": round(paper_size / (1024 * 1024), 2),
                "total_size_mb": round((topic_size + paper_size) / (1024 * 1024), 2),
                "expiry_hours": config.CACHE_EXPIRY_DAYS * 24
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get cache stats: {str(e)}")
            return {}
        
    def get_paper_cache(self, paper_id: str, data_type: str) -> Optional[Any]:
        """Retrieve cached data for a specific paper"""
        key = f"paper_{paper_id}_{data_type}"
        return self.get(key)

    def set_paper_cache(self, paper_id: str, data_type: str, value: Any) -> bool:
        """Cache data for a specific paper"""
        key = f"paper_{paper_id}_{data_type}"
        return self.set(key, value)
    
    
    def clear_expired_cache(self) -> dict:
        """
        Clear expired cache files
        
        Returns:
            Dictionary with count of deleted files by type
        """
        deleted = {"topics": 0, "papers": 0}
        
        try:
            # Clear expired topic cache
            for file in self.topic_cache_dir.glob("*.pkl"):
                file_age = datetime.now() - datetime.fromtimestamp(file.stat().st_mtime)
                if file_age > timedelta(hours=config.CACHE_EXPIRY_DAYS * 24):
                    file.unlink()
                    deleted["topics"] += 1
            
            # Clear expired paper cache
            for file in self.paper_cache_dir.glob("*.pkl"):
                file_age = datetime.now() - datetime.fromtimestamp(file.stat().st_mtime)
                if file_age > timedelta(hours=config.CACHE_EXPIRY_DAYS * 24):
                    file.unlink()
                    deleted["papers"] += 1
            
            total = deleted["topics"] + deleted["papers"]
            logger.info(f"Cleared {total} expired cache files")
            return deleted
            
        except Exception as e:
            logger.error(f"Failed to clear expired cache: {str(e)}")
            return deleted
        
    
    def clear_all_cache(self) -> dict:
        """
        Clear all cache files
        
        Returns:
            Dictionary with count of deleted files by type
        """
        deleted = {"topics": 0, "papers": 0}
        
        try:
            # Clear topic cache
            for file in self.topic_cache_dir.glob("*.pkl"):
                file.unlink()
                deleted["topics"] += 1
            
            # Clear paper cache
            for file in self.paper_cache_dir.glob("*.pkl"):
                file.unlink()
                deleted["papers"] += 1
            
            total = deleted["topics"] + deleted["papers"]
            logger.info(f"Cleared all {total} cache files")
            return deleted
            
        except Exception as e:
            logger.error(f"Failed to clear all cache: {str(e)}")
            return deleted


    def get_topic_cache(self, key: str, limit: int = None) -> Optional[List[Dict]]:
        """Get cached topic search results"""
        return self.get(key)

    def set_topic_cache(self, key: str, value: List[Dict], limit: int = None) -> None:
        """Cache topic search results"""
        self.set(key, value)

# Global cache manager instance
cache = CacheManager()
