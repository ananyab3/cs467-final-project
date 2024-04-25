from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from bs4 import BeautifulSoup
import csv
import time

def get_listings(driver, url):
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'article.placard')))
    time.sleep(1)  # Ensure the page has settled
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    apartment_listings = soup.select('article.placard')
    listings = []
    for apartment in apartment_listings:
        url = apartment.select_one('a.property-link')['href'] if apartment.select_one('a.property-link') else ''
        address = apartment.select_one('div.property-address').text.strip() if apartment.select_one('div.property-address') else ''
        price = apartment.select_one('p.property-pricing').text.strip() if apartment.select_one('p.property-pricing') else ''
        beds = apartment.select_one('p.property-beds').text.strip() if apartment.select_one('p.property-beds') else ''
        listings.append([address, price, beds, url])
    return listings

driver = webdriver.Chrome()
base_url = 'https://www.apartments.com/urbana-il/'
all_listings = get_listings(driver, base_url)

try:
    current_page = 0
    total_pages = 10  # Adjust as necessary
    while current_page < total_pages:
        pagination_links = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'nav.paging a[data-page]')))
        if current_page < len(pagination_links):
            try:
                page_url = pagination_links[current_page].get_attribute('href')
                if page_url:
                    all_listings.extend(get_listings(driver, page_url))
                current_page += 1
            except StaleElementReferenceException:
                print("StaleElementReferenceException caught, refetching elements")
                continue  # Refetch pagination links in the next loop iteration
        else:
            break
finally:
    driver.quit()

with open('apartments.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Address', 'Price', 'Beds', 'URL'])
    for listing in all_listings:
        writer.writerow(listing)

print("Scraping completed. Results saved to apartments.csv")
