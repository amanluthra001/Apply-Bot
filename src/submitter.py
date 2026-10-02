import asyncio
import json
import os
from playwright.async_api import async_playwright

async def apply_to_job(url: str, profile: dict, resume_path: str):
    """
    Automates the job application process for standard ATS forms like Lever and Greenhouse.
    """
    print(f"[*] Starting application for: {url}")
    print(f"[*] Using resume: {resume_path}")
    
    if not os.path.exists(resume_path):
        print(f"[!] Error: Resume file not found at {resume_path}")
        return False

    async with async_playwright() as p:
        # headless=True is REQUIRED for cloud servers since they don't have a monitor
        browser = await p.chromium.launch(headless=True) 
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            await page.goto(url, timeout=30000)
            
            # Very basic detection of ATS platform
            if "lever.co" in url:
                print("[*] Detected Lever form. Filling details...")
                await _fill_lever(page, profile, resume_path)
            elif "greenhouse.io" in url:
                print("[*] Detected Greenhouse form. Filling details...")
                await _fill_greenhouse(page, profile, resume_path)
            else:
                print("[!] Unsupported or generic job board. Skipping for now to avoid CAPTCHA.")
                return False
                
            # Click the final submit button (Cloud deployment means it applies automatically)
            print("[+] Form filled. Clicking Submit!")
            try:
                # Attempt to click standard submit buttons
                if "lever.co" in url:
                    await page.click("button[data-qa='btn-submit']")
                elif "greenhouse.io" in url:
                    await page.click("input[id='submit_app']")
                await page.wait_for_timeout(3000) # Wait for success page to load
            except Exception as e:
                print(f"[!] Warning: Could not click final submit automatically: {e}")

            print("[+] Application submitted successfully.")
            return True
            
        except Exception as e:
            print(f"[!] Application failed: {str(e)}")
            return False
        finally:
            await browser.close()


async def _fill_lever(page, profile, resume_path):
    """Fills a standard Lever application form"""
    # 1. Attach Resume
    await page.locator("input[type='file']").set_input_files(resume_path)
    await page.wait_for_timeout(2000) # Wait for upload
    
    # 2. Fill basic info (Lever usually has name='name', name='email', name='phone')
    await fill_if_exists(page, "input[name='name']", f"{profile['first_name']} {profile['last_name']}")
    await fill_if_exists(page, "input[name='email']", profile['email'])
    await fill_if_exists(page, "input[name='phone']", profile['phone'])
    await fill_if_exists(page, "input[name='org']", profile['current_company'])
    
    # 3. Fill URLs
    await fill_if_exists(page, "input[name='urls[LinkedIn]']", profile['linkedin_url'])
    await fill_if_exists(page, "input[name='urls[GitHub]']", profile['github_url'])
    await fill_if_exists(page, "input[name='urls[Portfolio]']", profile['portfolio_url'])

async def _fill_greenhouse(page, profile, resume_path):
    """Fills a standard Greenhouse application form"""
    # 1. Attach Resume (Greenhouse usually has a specific input or button)
    try:
        await page.locator("input[type='file']").first.set_input_files(resume_path)
        await page.wait_for_timeout(2000)
    except:
        print("[!] Could not find resume upload button for Greenhouse.")
        
    # 2. Fill basic info
    await fill_if_exists(page, "input#first_name", profile['first_name'])
    await fill_if_exists(page, "input#last_name", profile['last_name'])
    await fill_if_exists(page, "input#email", profile['email'])
    await fill_if_exists(page, "input#phone", profile['phone'])
    
    # 3. Fill custom URLs (Greenhouse often uses custom questions for links)
    # This requires more advanced scraping to detect the question label, but we try standard inputs:
    await fill_if_exists(page, "input[autocomplete='custom-question-linkedin']", profile['linkedin_url'])

async def fill_if_exists(page, selector, text):
    """Helper to fill a field only if it exists on the page"""
    try:
        element = page.locator(selector)
        if await element.count() > 0:
            await element.first.fill(text)
    except:
        pass
