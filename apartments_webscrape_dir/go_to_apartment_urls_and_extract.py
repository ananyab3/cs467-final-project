import csv
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def clean_address(address):
    lines = address.split('\n')
    cleaned_lines = [line.strip() for line in lines if line.strip()]

    full_address = ' '.join(cleaned_lines)
    
    normalized_address = full_address.replace(' – ', ' - ')

    cleaned_address = ""
    if '-' in normalized_address:
        cleaned_address = normalized_address.split(" - ")[0].strip()
    else:
        cleaned_address = full_address

    cleaned_address_commas = cleaned_address.replace(" ," , ",") 

    return cleaned_address_commas

def clean_price(price):
    if "/ Person" in price:
        clean_price = price.split("/ Person")[0].strip()
    else:
        clean_price = price
    return clean_price

def scrape_data(driver, url):
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'propertyAddressContainer')))
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    address_container = soup.select_one('.propertyAddressContainer h2')
    if address_container:
        address = clean_address(address_container.get_text(separator="\n"))
    else:
        address = 'Address Not Found'

    data = []
    apartment_options = soup.select('.pricingGridItem')
    for option in apartment_options:
        price = clean_price(option.find('span', class_='rentLabel').text.strip() if option.find('span', class_='rentLabel') else 'Price Not Listed')
        bedrooms = option.find('span', class_='detailsTextWrapper').find('span').text.strip() if option.find('span', class_='detailsTextWrapper') else 'Bed Info Not Available'
        data.append([address, price, bedrooms, "apartments.com", url])

    return data

chrome_options = webdriver.ChromeOptions()
#chrome_options.add_argument("--headless") # Ensures Chrome runs in headless mode
driver = webdriver.Chrome(options=chrome_options)

with open('only_url_data.csv', mode='r', encoding='utf-8') as file:
    csv_reader = csv.DictReader(file)
    urls = [row['URL'] for row in csv_reader if 'URL' in row and row['URL']]

with open('apartments_clean7_dataset.csv', mode='w', encoding='utf-8', newline='') as file:
    csv_writer = csv.writer(file)
    csv_writer.writerow(['Address', 'Price', 'Bedrooms', 'Source', 'URL']) # Header
    for url in urls:
        try:
            apartment_data = scrape_data(driver, url)
            csv_writer.writerows(apartment_data)
        except TimeoutException:
            print(f"Timeout occurred while loading page {url}. Check page load strategy or increase timeout.")
        except Exception as e:
            print(f"An error occurred while scraping {url}: {str(e)}")
            import traceback
            print(traceback.format_exc())

driver.quit()
print("Scraping completed and results saved to updated_data.csv.")