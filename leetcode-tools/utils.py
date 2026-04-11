"""
Shared utilities for LeetCode tools.
=====================================
Common functions used by both Doctor and Suggestor.
"""

from typing import Iterator, TypeVar

T = TypeVar('T')


def chunk_items(items: list[T], chunk_size: int) -> Iterator[list[T]]:
    """Split a list into chunks of specified size.
    
    Shared between Doctor and Suggestor to avoid duplication.
    
    Args:
        items: List of items to chunk
        chunk_size: Maximum size of each chunk
        
    Yields:
        Lists of items, each with length <= chunk_size
    """
    chunk = []
    for item in items:
        chunk.append(item)
        if len(chunk) == chunk_size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk
