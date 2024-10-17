from functools import lru_cache

summary_cache = {}

@lru_cache(maxsize=100)
def get_cached_summary(file_hash: str):
    """Retrieve the cached summary for the given file hash if it exists."""
    return summary_cache.get(file_hash)

def cache_summary(file_hash: str, summary: str):
    """Cache the summary of the JSON data associated with a file hash."""
    summary_cache[file_hash] = summary