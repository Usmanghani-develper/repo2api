"""Code analysis engine for repository analysis."""

import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from backend.core.parser import ParserFactory
from backend.core.utils import (
    get_python_files,
    get_timestamp,
    is_directory_too_large,
)
from backend.models import FunctionInfo, RepositoryAnalysis

logger = logging.getLogger(__name__)


class CodeAnalyzer:
    """Analyzes repositories and extracts function information."""
    
    def __init__(self, language: str = 'python', max_repo_size_mb: int = 500):
        """
        Initialize code analyzer.
        
        Args:
            language: Programming language to analyze
            max_repo_size_mb: Maximum repository size in MB
        """
        self.language = language
        self.max_repo_size_mb = max_repo_size_mb
        self.parser = ParserFactory.create_parser(language)
    
    def analyze_repository(
        self,
        repo_path: Path,
        repo_name: str,
        repo_url: Optional[str] = None
    ) -> RepositoryAnalysis:
        """
        Analyze a repository and extract function information.
        
        Args:
            repo_path: Path to repository
            repo_name: Name of repository
            repo_url: URL of repository (optional)
            
        Returns:
            RepositoryAnalysis object
        """
        logger.info(f"Starting analysis of repository: {repo_name}")
        
        errors = []
        functions: List[FunctionInfo] = []
        
        # Check repository size
        if is_directory_too_large(repo_path, self.max_repo_size_mb):
            msg = f"Repository exceeds maximum size of {self.max_repo_size_mb}MB"
            logger.error(msg)
            errors.append(msg)
            return RepositoryAnalysis(
                repository_name=repo_name,
                repository_url=repo_url,
                total_functions=0,
                functions=[],
                analysis_timestamp=get_timestamp(),
                language=self.language,
                errors=errors
            )
        
        # Get all source files
        if self.language == 'python':
            source_files = get_python_files(repo_path)
        else:
            logger.error(f"Unsupported language: {self.language}")
            errors.append(f"Unsupported language: {self.language}")
            source_files = []
        
        logger.info(f"Found {len(source_files)} source files")
        
        # Analyze each file
        for file_path in source_files:
            try:
                logger.debug(f"Analyzing file: {file_path}")
                file_functions = self.parser.parse_file(file_path)
                functions.extend(file_functions)
                logger.debug(f"Found {len(file_functions)} functions in {file_path}")
            except Exception as e:
                error_msg = f"Error analyzing {file_path}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        logger.info(f"Analysis complete. Found {len(functions)} total functions")
        
        return RepositoryAnalysis(
            repository_url=repo_url,
            repository_name=repo_name,
            total_functions=len(functions),
            functions=functions,
            analysis_timestamp=get_timestamp(),
            language=self.language,
            errors=errors
        )
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        return ParserFactory.supported_languages()


class AnalysisCache:
    """Simple in-memory cache for analysis results."""
    
    def __init__(self, max_entries: int = 100):
        """
        Initialize cache.
        
        Args:
            max_entries: Maximum number of cached entries
        """
        self.cache = {}
        self.max_entries = max_entries
    
    def get(self, key: str) -> Optional[RepositoryAnalysis]:
        """
        Get analysis from cache.
        
        Args:
            key: Cache key
            
        Returns:
            RepositoryAnalysis or None
        """
        return self.cache.get(key)
    
    def set(self, key: str, analysis: RepositoryAnalysis) -> None:
        """
        Store analysis in cache.
        
        Args:
            key: Cache key
            analysis: RepositoryAnalysis to cache
        """
        if len(self.cache) >= self.max_entries:
            # Remove oldest entry
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[key] = analysis
    
    def clear(self) -> None:
        """Clear the cache."""
        self.cache.clear()
    
    def size(self) -> int:
        """Get cache size."""
        return len(self.cache)
