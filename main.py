import asyncio
import json
import os
import re
from src.classifier import categorize_job
from src.submitter import apply_to_job

def load_profile():
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'profile.json')
    with open(config_path, 'r') as f:
        return json.load(f)

def extract_urls_from_text(text: str):
    """Extracts all URLs from a given block of text (like a WhatsApp message)"""
    url_pattern = re.compile(r'https?://[^\s]+')
    return url_pattern.findall(text)

async def process_job_queue(urls, profile):
    """Processes a list of URLs sequentially"""
    for url in urls:
        print(f"\n{'='*50}\nProcessing: {url}\n{'='*50}")
        
        # 1. Very basic title extraction (In a real scenario, we'd scrape the page title first)
        # For now, we'll extract keywords from the URL itself to guess the role if we don't scrape it
        guessed_category = categorize_job(title=url)
        print(f"[*] AI/Classifier determined best resume: {guessed_category.upper()}")
        
        # 2. Get the correct resume path
        # Fix paths relative to main.py
        raw_resume_path = profile['resume_paths'][guessed_category]
        resume_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config', raw_resume_path))
        
        # 3. Apply
        success = await apply_to_job(url, profile, resume_path)
        if success:
            print("[+] Successfully processed.")
        else:
            print("[-] Failed to process or skipped.")

import time
import os
from src.fetcher import get_dynamic_job_links

def load_applied_urls():
    memory_file = os.path.join(os.path.dirname(__file__), 'applied_jobs.txt')
    if not os.path.exists(memory_file):
        return set()
    with open(memory_file, 'r') as f:
        return set(line.strip() for line in f)

def save_applied_url(url):
    memory_file = os.path.join(os.path.dirname(__file__), 'applied_jobs.txt')
    with open(memory_file, 'a') as f:
        f.write(url + '\n')

def main():
    print("🚀 Auto-Apply Bot Initialized (Cloud / Autonomous Mode)")
    profile = load_profile()
    
    # Check resumes folder
    resumes_dir = os.path.join(os.path.dirname(__file__), 'resumes')
    if not os.path.exists(resumes_dir):
        os.makedirs(resumes_dir)
        print(f"[!] Created {resumes_dir}. Please place your PDF resumes there.")
    
    applied_urls = load_applied_urls()
    print(f"[*] Memory loaded. You have previously applied to {len(applied_urls)} jobs.")
    
    # For GitHub actions / cloud, we don't loop infinitely, we just run once and let the cloud cron trigger it
    print("\n" + "="*50)
    urls = get_dynamic_job_links()
    
    # Filter out jobs we already processed
    new_urls = [u for u in urls if u not in applied_urls]
    
    if not new_urls:
        print("[*] No new job postings found right now.")
    else:
        print(f"[*] Found {len(new_urls)} new job links. Starting automation...\n")
        
        # Run the async queue
        asyncio.run(process_job_queue(new_urls, profile))
        
        # Mark as applied
        for u in new_urls:
            save_applied_url(u)
            
        print("[*] Finished applying to the current batch.")


if __name__ == "__main__":
    main()
