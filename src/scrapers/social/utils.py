import re

def parse_social_stats(text):
    """
    Robust regex parser for social media stats in search engine snippets.
    Extracted from the 'content' field of SearXNG results or meta tags.
    """
    if not text: return None
    
    stats = {}
    # Patterns for Followers: "10K Followers", "2.5M followers", "500 followers"
    follower_patterns = [
        r'([\d\.,KkMmBb]+?)\s+[Ff]ollowers',
        r'[Ff]ollowers:\s*([\d\.,KkMmBb]+)',
        r'([\d\.,KkMmBb]+?)\s+[Ss]ubscribers',
        r'([\d\.,KkMmBb]+?)\s+abonnés', # French
        r'([\d\.,KkMmBb]+?)\s+[Ff]olger', # German
        r'([\d\.,KkMmBb]+?)\s+seguidores', # Spanish/Portuguese
        r'([\d\.,KkMmBb]+?)\s+Followers'
    ]
    
    for pattern in follower_patterns:
        match = re.search(pattern, text)
        if match:
            # Clean up: remove trailing dots and uppercase
            val = match.group(1).rstrip('.').upper()
            stats["followers"] = val
            break
            
    # Patterns for Following/Posts if available
    following_match = re.search(r'([\d\.,KkMmBb]+?)\s+[Ff]ollowing', text)
    if following_match:
        stats["following"] = following_match.group(1).rstrip('.').upper()
        
    posts_match = re.search(r'([\d\.,KkMmBb]+?)\s+[Pp]osts', text)
    if posts_match:
        stats["posts"] = posts_match.group(1).rstrip('.').upper()

    return stats if stats else None
