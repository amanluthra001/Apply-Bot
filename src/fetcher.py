import requests
import re
import html

def get_dynamic_job_links():
    """
    Searches Hacker News dynamically for recently posted tech jobs 
    specifically on Lever and Greenhouse.
    """
    print("[*] AI is actively searching tech forums (Hacker News) for new job postings...")
    
    job_links = []
    queries = ['jobs.lever.co', 'boards.greenhouse.io']
    url_pattern = re.compile(r'https://(?:jobs\.lever\.co|boards\.greenhouse\.io)/[^\s\"\'<>]+')
    
    for q in queries:
        print(f"[*] Querying API for: {q}")
        try:
            # Get the latest 50 hits mentioning the job board
            r = requests.get(f'https://hn.algolia.com/api/v1/search_by_date?query={q}&hitsPerPage=50')
            if r.status_code == 200:
                data = r.json()
                for hit in data.get('hits', []):
                    raw_text = hit.get('comment_text') or hit.get('story_text') or hit.get('title') or ""
                    text = html.unescape(raw_text)
                    
                    raw_url = hit.get('url') or ""
                    url_field = html.unescape(raw_url)
                    
                    found_urls = url_pattern.findall(text) + url_pattern.findall(url_field)
                    job_links.extend(found_urls)
        except Exception as e:
            print(f"[!] Search error: {e}")
            
    # Filter links to make sure they are actual job postings
    valid_links = []
    for link in job_links:
        # Clean up trailing punctuation from regex
        link = link.rstrip('.,;)]}')
        if 'jobs.lever.co/' in link and len(link.split('/')) >= 4:
            valid_links.append(link)
        elif 'boards.greenhouse.io/' in link and len(link.split('/')) >= 4:
            valid_links.append(link)
            
    unique_links = list(set(valid_links))
    print(f"[*] Found {len(unique_links)} potential job links.")
    return unique_links

if __name__ == "__main__":
    print(get_dynamic_job_links())
