from playwright.sync_api import sync_playwright
from dataclasses import dataclass
import pandas as pd
import os

google_map_links = [
    "https://www.google.com/maps/place/Drive+Today+Ontario/@43.4941087,-79.6469693,17z/data=!3m1!4b1!4m6!3m5!1s0x882b45c865c9f07b:0xae5381bc7ceff817!8m2!3d43.4941087!4d-79.6469693!16s%2Fg%2F11fktfrcr9?entry=ttu",
    "https://www.google.com/maps/place/Manjoo+Restaurant/@33.5507336,73.1248027,15z/data=!4m2!3m1!1s0x0:0x7efae6771835d403?sa=X&ved=1t:2428&ictx=111"
]

@dataclass
class Business:
    name: str = None
    address: str = None
    website: str = None
    phone_number: str = None

def extract_business_details(page):
    def clean_text(text):
        if text:
            return text.split('\n', 1)[-1].strip()
        return None

    business = Business()
    business.name = clean_text(page.query_selector(".lfPIob").inner_text()) if page.query_selector(".lfPIob") else None
    business.address = clean_text(page.query_selector("button[data-item-id='address'] div").inner_text()) if page.query_selector("button[data-item-id='address'] div") else None
    business.website = clean_text(page.query_selector("a[data-item-id='authority'] div").inner_text()) if page.query_selector("a[data-item-id='authority'] div") else None
    business.phone_number = clean_text(page.query_selector("button[data-tooltip='Copy phone number'] div").inner_text()) if page.query_selector("button[data-tooltip='Copy phone number'] div") else None
    return business

def scrape_all_businesses(urls):
    all_businesses = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        for url in urls:
            page.goto(url, timeout=60000)
            page.wait_for_timeout(5000)  
            business_details = extract_business_details(page)
            all_businesses.append(business_details)
        browser.close()
    return all_businesses

def save_to_csv(businesses):
    business_dicts = [business.__dict__ for business in businesses]
    df = pd.DataFrame(business_dicts)
    directory = 'output-of-scrape-with-link'
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = os.path.join(directory, 'business_details.csv')
    df.to_csv(file_path, index=False)
    print(f"File saved at {file_path}")

if __name__ == "__main__":
    businesses = scrape_all_businesses(google_map_links)
    save_to_csv(businesses)
