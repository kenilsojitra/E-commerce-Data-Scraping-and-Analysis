import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

def flipkart_scraper(item_to_scrape, data_number):
    try:
        data_number = int(data_number)
    except ValueError:
        print("Error: data_number must be an integer.")
        return

    base_url = f"https://www.flipkart.com/search?q={item_to_scrape}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    product_title = []
    product_mrp = []
    product_rating = []
    product_img = []

    page_number = 1
    while len(product_title) < data_number:
        print(f"Fetching page {page_number}")
        response = requests.get(f"{base_url}&page={page_number}", headers=headers)
        if response.status_code != 200:
            print(f"Failed to retrieve page {page_number}, status code: {response.status_code}")
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        products = soup.find_all("div", class_="_1AtVbE")
        if not products:
            print(f"No products found on page {page_number}.")
            break

        for product in products:
            if len(product_title) >= data_number:
                break

            try:
                title_elem = product.find("a", class_="IRpwTa")
                title = title_elem.get_text(strip=True) if title_elem else "No title found"
                product_title.append(title)
            except Exception as e:
                print(f"Error extracting title: {e}")
                product_title.append("No title found")

            try:
                mrp_elem = product.find("div", class_="_30jeq3")
                mrp = mrp_elem.get_text(strip=True) if mrp_elem else "No price found"
                product_mrp.append(mrp)
            except Exception as e:
                print(f"Error extracting price: {e}")
                product_mrp.append("No price found")

            try:
                rating_elem = product.find("span", class_="_3LWZlK")
                rating = rating_elem.get_text(strip=True) if rating_elem else "No rating found"
                product_rating.append(rating)
            except Exception as e:
                print(f"Error extracting rating: {e}")
                product_rating.append("No rating found")

            try:
                image_elem = product.find("img", class_="_396cs4")
                image_url = image_elem['src'] if image_elem else "No image found"
                product_img.append(image_url)
            except Exception as e:
                print(f"Error extracting image URL: {e}")
                product_img.append("No image found")

        page_number += 1

    print("Scraping completed.")

    print("Saving data to CSV...")
    if len(product_title) > 0:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{item_to_scrape}_{timestamp}.csv"
        output_directory = "csv_folder"
        
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        
        df = pd.DataFrame({
            "Product Title": product_title,
            "Product Price": product_mrp,
            "Product Rating": product_rating,
            "Product Image URL": product_img,
        })
        df.to_csv(os.path.join(output_directory, file_name), index=True)
    else:
        print("No products scraped")

    print("Finally Scraping completed")

# Example usage
flipkart_scraper("laptop", 20)
