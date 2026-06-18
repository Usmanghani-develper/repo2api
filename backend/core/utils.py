"""Utility functions for Repo2API."""

import os
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from urllib.parse import urlparse
import subprocess

logger = logging.getLogger(__name__)


def get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.utcnow().isoformat() + "Z"


def sanitize_function_name(name: str) -> str:
    """Sanitize function name for use in URL paths."""
    return name.replace("_", "-").lower()


def is_github_url(url: str) -> bool:
    """Check if a URL is a valid GitHub repository URL."""
    try:
        parsed = urlparse(url)
        return "github.com" in parsed.netloc
    except Exception:
        return False


def clone_repository(repo_url: str, destination: Path) -> bool:
    """
    Clone a GitHub repository to a local destination.
    
    Args:
        repo_url: GitHub repository URL
        destination: Local destination path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if destination.exists():
            logger.warning(f"Destination {destination} already exists, removing...")
            shutil.rmtree(destination)
        
        logger.info(f"Cloning repository from {repo_url}...")
        result = subprocess.run(
            ["git", "clone", repo_url, str(destination)],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode != 0:
            logger.error(f"Failed to clone repository: {result.stderr}")
            return False
        
        logger.info(f"Successfully cloned repository to {destination}")
        return True
    except Exception as e:
        logger.error(f"Error cloning repository: {e}")
        return False


def get_python_files(directory: Path, ignore_patterns: List[str] = None) -> List[Path]:
    """
    Recursively find all Python files in a directory.
    
    Args:
        directory: Root directory to search
        ignore_patterns: Patterns to ignore
        
    Returns:
        List of Python file paths
    """
    if ignore_patterns is None:
        ignore_patterns = [
            "node_modules",
            ".git",
            "__pycache__",
            ".venv",
            "venv",
            ".env",
            ".DS_Store",
        ]
    
    python_files = []
    
    try:
        for root, dirs, files in os.walk(directory):
            # Remove ignored directories
            dirs[:] = [
                d for d in dirs
                if not any(pattern in d for pattern in ignore_patterns)
            ]
            
            # Find Python files
            for file in files:
                if file.endswith(".py"):
                    filepath = Path(root) / file
                    python_files.append(filepath)
    except Exception as e:
        logger.error(f"Error scanning directory {directory}: {e}")
    
    return sorted(python_files)


def get_directory_size(path: Path) -> int:
    """
    Get total size of a directory in bytes.
    
    Args:
        path: Directory path
        
    Returns:
        Total size in bytes
    """
    total = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total += os.path.getsize(filepath)
    except Exception as e:
        logger.error(f"Error calculating directory size: {e}")
    
    return total


def is_directory_too_large(path: Path, max_size_mb: int = 500) -> bool:
    """
    Check if directory size exceeds maximum.
    
    Args:
        path: Directory path
        max_size_mb: Maximum size in MB
        
    Returns:
        True if directory is too large
    """
    size_bytes = get_directory_size(path)
    size_mb = size_bytes / (1024 * 1024)
    return size_mb > max_size_mb


def extract_repo_name(url: str) -> str:
    """
    Extract repository name from GitHub URL.
    
    Args:
        url: GitHub repository URL
        
    Returns:
        Repository name
    """
    # Handle various GitHub URL formats
    url = url.rstrip("/").replace(".git", "")
    parts = url.split("/")
    if len(parts) >= 2:
        return parts[-1]
    return "repository"


def create_directory_if_not_exists(path: Path) -> bool:
    """
    Create directory if it doesn't exist.
    
    Args:
        path: Directory path
        
    Returns:
        True if successful
    """
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating directory {path}: {e}")
        return False


def clean_cache_directory(cache_dir: Path, keep_latest: int = 5) -> bool:
    """
    Clean up old cached repositories.
    
    Args:
        cache_dir: Cache directory path
        keep_latest: Number of latest repos to keep
        
    Returns:
        True if successful
    """
    try:
        if not cache_dir.exists():
            return True
        
        # Get all subdirectories sorted by creation time
        subdirs = sorted(
            cache_dir.iterdir(),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        # Remove old directories
        for subdir in subdirs[keep_latest:]:
            if subdir.is_dir():
                logger.info(f"Removing old cache: {subdir}")
                shutil.rmtree(subdir)
        
        return True
    except Exception as e:
        logger.error(f"Error cleaning cache: {e}")
        return False


def normalize_path(path: str) -> Path:
    """
    Normalize a path string to a Path object.
    
    Args:
        path: Path string
        
    Returns:
        Normalized Path object
    """
    return Path(path).expanduser().resolve()


def is_valid_python_identifier(name: str) -> bool:
    """
    Check if a string is a valid Python identifier.
    
    Args:
        name: String to check
        
    Returns:
        True if valid identifier
    """
    return name.isidentifier()


def merge_dicts(*dicts) -> dict:
    """
    Merge multiple dictionaries.
    
    Args:
        *dicts: Dictionaries to merge
        
    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    return result
