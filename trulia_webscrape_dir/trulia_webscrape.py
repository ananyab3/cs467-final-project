import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
import re
import time
from selenium.common.exceptions import TimeoutException
import random

def clean_price(price_str):
    return re.sub(r'[^0-9-]', '', price_str)

def check_and_handle_popup(driver):
    try:
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@aria-label, 'Press & Hold')]"))
        )
        print("Press & Hold button found. Skipping this page for now.")
        return False
    except TimeoutException:
        print("Press & Hold button not found. Proceeding with scraping.")
        return True

def random_scroll(driver, delay):
    scroll_pause_time = 0.5
    screen_height = driver.execute_script("return window.innerHeight")
    scroll_height = driver.execute_script("return document.body.scrollHeight")
    
    for _ in range(int(delay / scroll_pause_time)):
        scroll_position = random.randint(0, scroll_height - screen_height)
        driver.execute_script(f"window.scrollTo(0, {scroll_position});")
        time.sleep(scroll_pause_time)

def get_listings(driver, url):
    driver.get(url)
    
    # if not check_and_handle_popup(driver):
    #     return []
    
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li[data-testid^="srp-home-card-"]'))
        )
    except TimeoutException:
        print("Timed out waiting for property cards to load. Skipping this page.")
        return []
    
    scroll_pause_time = 0.2
    screen_height = driver.execute_script("return window.innerHeight")
    i = 1

    while True:
        # Scroll one viewport at a time, pausing to allow content to load
        driver.execute_script(f"window.scrollTo(0, {screen_height * i});")
        i += 1
        time.sleep(scroll_pause_time)
        # Check if we've reached the bottom of the page
        scroll_height = driver.execute_script("return document.body.scrollHeight")
        if (screen_height * i) > scroll_height:
            break  # If so, exit the loop

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    property_cards = soup.select('li[data-testid^="srp-home-card-"]')
    print(f"Found {len(property_cards)} property cards after scrolling")

    listings = []

    for card in property_cards:
        print("Processing card...")
        address = card.select_one('div[data-testid="property-address"]')
        price = card.select_one('div[data-testid="property-price"]')
        beds = card.select_one('div[data-testid="property-beds"]')

        if address and price and beds:
            address = address.text.strip()
            price = price['title']
            beds = beds.text.strip()

            price_clean = clean_price(price)
            listing = [address, price_clean, beds, "Trulia"]
            listings.append(listing)
            print(f"Added listing: {listing}")
        else:
            print("Skipping card due to missing data")
    
    print(f"Collected {len(listings)} listings")
    return listings


def main(args):
    chrome_options = webdriver.ChromeOptions()
    if args.headless:
        chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(options=chrome_options)
    base_url = args.base_url
    start_page = args.start_page
    end_page = args.end_page
    delay = args.delay
    output_file = args.output_file
    scraped_pages_file = args.scraped_pages_file
    skipped_pages_file = args.skipped_pages_file

    scraped_pages = []
    skipped_pages = []

    with open(output_file, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Address', 'Price', 'Beds', 'Source'])

        for page in range(start_page, end_page + 1):
            url = base_url + (f"{page}_p/" if page > 1 else "")
            print(f"Scraping page {page}...")
            
            listings = get_listings(driver, url)
            if listings:
                writer.writerows(listings)
                csvfile.flush()
                scraped_pages.append(page)
            else:
                skipped_pages.append(page)
            
            #print(f"Waiting for {delay} seconds before scraping the next page...")
            random_scroll(driver, delay)

    driver.quit()

    print(f"Scraping completed. Results saved to {output_file}")

    
    with open(scraped_pages_file, 'a') as file:
        file.write('\n'.join(map(str, scraped_pages)))

    with open(skipped_pages_file, 'a') as file:
        file.write('\n'.join(map(str, skipped_pages)))

    print("Scraped and skipped page numbers saved to files.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape rental listings from Trulia.")
    parser.add_argument("--base_url", type=str, default="https://www.trulia.com/for_rent/Urbana,IL/", help="Base URL for the search results")
    parser.add_argument("--start_page", type=int, default=1, help="Starting page number")
    parser.add_argument("--end_page", type=int, default=100, help="Ending page number")
    parser.add_argument("--delay", type=int, default=120, help="Delay in seconds between scraping each page")
    parser.add_argument("--output_file", type=str, default="trulia_rentals.csv", help="Output CSV file name")
    parser.add_argument("--scraped_pages_file", type=str, default="scraped_pages.txt", help="File to store scraped page numbers")
    parser.add_argument("--skipped_pages_file", type=str, default="skipped_pages.txt", help="File to store skipped page numbers")
    parser.add_argument("--headless", action="store_true", help="Run the browser in headless mode")

    args = parser.parse_args()

    main(args)