from googlesearch import search
import time

def get_dynamic_job_links():
    """
    Searches Google dynamically for recently posted tech jobs 
    specifically on Lever and Greenhouse (since our bot knows how to fill these).
    """
    print("[*] AI is actively searching the web for new job postings...")
    
    # We target entry-level/fresher SDE roles
    queries = [
        'site:jobs.lever.co "software" (intern OR fresher OR "entry level" OR "new grad")',
        'site:boards.greenhouse.io "software" (intern OR fresher OR "entry level" OR "new grad")',
        'site:jobs.lever.co "data" (intern OR fresher OR "entry level")',
        'site:boards.greenhouse.io "machine learning" (intern OR fresher OR "entry level")'
    ]
    
    job_links = []
    
    for q in queries:
        print(f"[*] Querying: {q}")
        try:
            # sleep_interval prevents Google from blocking us for spam
            for url in search(q, num_results=5, sleep_interval=2):
                job_links.append(url)
        except Exception as e:
            print(f"[!] Search error: {e}")
            
    # Filter links to make sure they are actual job postings and not just company homepages
    valid_links = []
    for link in job_links:
        if 'jobs.lever.co/' in link and len(link.split('/')) >= 4:
            valid_links.append(link)
        elif 'boards.greenhouse.io/' in link and len(link.split('/')) >= 4:
            valid_links.append(link)
            
    # Remove duplicates
    unique_links = list(set(valid_links))
    print(f"[*] Found {len(unique_links)} potential job links.")
    return unique_links

if __name__ == "__main__":
    print(get_dynamic_job_links())
