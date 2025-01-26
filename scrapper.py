import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import logging

def init_driver():
    """
    Initialize the Selenium WebDriver with specific options.

    Returns:
        WebDriver: Configured Selenium WebDriver instance.
    """
    options = Options()
    options.add_argument("--headless")  # Run the browser in headless mode (no GUI).
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service('/usr/local/bin/chromedriver')  # Path to the ChromeDriver executable.
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(10)  # Implicit wait time of 10 seconds for element detection.
    return driver

def scrape_all_product_links(driver, base_url):
    """
    Extracts all product links from all pages.

    Args:
        driver (WebDriver): Selenium WebDriver instance.
        base_url (str): Base URL of the main page to scrape.

    Returns:
        list: List of product links (URLs).
    """
    product_links = []
    page = 1
    while True:
        print(f"Scraping page {page}...")
        driver.get(f"{base_url}catalogue/page-{page}.html")
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "h3 a"))
            )
            product_elements = driver.find_elements(By.CSS_SELECTOR, "h3 a")
            if not product_elements:
                break  # Stop if no more products found
            product_links.extend([elem.get_attribute('href') for elem in product_elements])
            page += 1
        except Exception as e:
            print(f"Error on page {page}: {e}")
            break
    return product_links

def scrape_product_details(driver, product_url):
    """
    Extracts details of a product given its URL.

    Args:
        driver (WebDriver): Selenium WebDriver instance.
        product_url (str): URL of the product page to scrape.

    Returns:
        dict: Dictionary containing product details or None if an error occurs.
    """
    driver.get(product_url)
    try:
        # Extract product information
        name = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1"))
        ).text.strip().lower()
        price = driver.find_element(By.CSS_SELECTOR, "p.price_color").text.strip().replace("£", "")
        price = float(price)  # Convert price to a float
        description = driver.find_element(By.CSS_SELECTOR, "#product_description ~ p").text.strip().lower()
        category = driver.find_element(By.CSS_SELECTOR, "ul.breadcrumb li:nth-child(3) a").text.strip().lower()

        # Attempt to extract stock information if available
        try:
            stock = driver.find_element(By.CSS_SELECTOR, "p.in-stock.availability").text.strip()
        except NoSuchElementException:
            stock = "In stock"  # Default value if stock information is not found

        return {
            "name": name,
            "price": price,
            "description": description,
            "category": category,
            "stock": stock,
            "url": product_url
        }
    except Exception as e:
        logging.error(f"Error extracting details from {product_url}: {e}")
        return None

def save_to_csv(data, filename="products.csv"):
    """
    Saves scraped data to a CSV file.

    Args:
        data (list): List of dictionaries containing product data.
        filename (str): Name of the output CSV file.

    Returns:
        None
    """
    if not data:
        print("No data to save.")
        return
    keys = data[0].keys()  # Use keys of the first item as headers
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    print(f"Data successfully saved to '{filename}'.")

def main():
    """
    Main function to run the scraper. Extracts product links, scrapes product details,
    and saves the data to a CSV file.
    """
    base_url = "http://books.toscrape.com/"
    logging.basicConfig(
        filename="scraper.log",
        level=logging.ERROR,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    driver = init_driver()
    print("Starting the scraper...")

    try:
        print("Retrieving product links...")
        product_links = scrape_all_product_links(driver, base_url)
        print(f"Found {len(product_links)} products.")

        products = []
        for i, link in enumerate(product_links):
            if i > 0 and i % 10 == 0:  # Restart driver every 10 products
                driver.quit()
                driver = init_driver()

            print(f"Scraping product {i + 1}/{len(product_links)}: {link}")
            product_details = scrape_product_details(driver, link)
            if product_details:
                products.append(product_details)

        # Save the product data to a CSV file
        save_to_csv(products)

    except Exception as e:
        print(f"General error: {e}")
    finally:
        driver.quit()
        print("Scraper finished.")

if __name__ == "__main__":
    main()

