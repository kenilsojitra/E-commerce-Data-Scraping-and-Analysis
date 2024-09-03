from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
from bs4 import BeautifulSoup
import os

def myntra_scraper(item_to_scrape, data_number, file_name):
    data_number = int(data_number) * 3  # To ensure we get enough clean data
    
    url = f"https://www.myntra.com/{item_to_scrape}"
    service = Service(executable_path="D:\\projects python django\\scraper\\home\\chromedriver.exe")
    driver = webdriver.Chrome(service=service)
    
    product_title = []
    product_mrp = []
    product_discounted_price = []
    product_img = []
    product = [] 
    product_url = []
    product_rating = []
    product_rating_count = []

    # Load existing data if the CSV file already exists
    output_directory = "csv_folder"
    output_path = os.path.join(output_directory, file_name + ".csv")
    if os.path.exists(output_path):
        existing_data = pd.read_csv(output_path)
        # Convert to list of dictionaries for easy appending
        existing_data_dict = existing_data.to_dict(orient='records')
    else:
        existing_data_dict = []

    while len(product_title) < data_number:
        page_num = 1  # Start from page 1 for each new scraping run
        while len(product_title) < data_number:
            page_url = f"https://www.myntra.com/{item_to_scrape}?p={page_num}"
            driver.get(page_url)
            time.sleep(3)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            products = soup.select(".product-base")

            if not products:
                print(f"No products found on page {page_num}. Ending scraping for item.")
                break

            for product in products:
                if len(product_title) >= data_number:
                    break

                try:
                    title = product.select_one('.product-product')
                    title_text = title.get_text(strip=True) if title else "No title found"
                    product_title.append(title_text)
                except:
                    product_title.append("No title found")

                try:
                    mrp = product.select_one('.product-strike')
                    mrp_text = mrp.get_text(strip=True) if mrp else "No MRP found"
                    product_mrp.append(mrp_text)

                    discounted_price = product.select_one('.product-discountedPrice')
                    discounted_price_text = discounted_price.get_text(strip=True) if discounted_price else "No discounted price found"
                    product_discounted_price.append(discounted_price_text)
                except:
                    product_mrp.append("No MRP found")
                    product_discounted_price.append("No discounted price found")

                try:
                    image = product.select_one('picture img')
                    if image:
                        image_url = image['src']
                    else:
                        image = product.select_one('img')
                        image_url = image['src'] if image else "No image found"
                        if image_url == "No image found":
                            image = product.select_one('img')['data-src']
                            image_url = image['data-src'] if image else "No image found"
                    image_url = f"https://assets.myntassets.com/{image_url}" if image_url != "No image found" else image_url
                    product_img.append(image_url)
                except:
                    product_img.append("No image found")

                try:
                    rating = product.select_one('.product-ratingsContainer')
                    rating_text = rating.get_text(strip=True) if rating else "No rating found"
                    rating_text = rating_text.split('|')[0].strip() if rating_text != "No rating found" else "No rating found"
                    product_rating.append(rating_text)

                    rating_count = product.select_one('.product-ratingsCount')
                    rating_count_text = rating_count.get_text(strip=True) if rating_count else "No rating count found"
                    rating_count_text = rating_count_text.split('|')[1].strip() if rating_count_text != "No rating count found" else "No rating count found"
                    product_rating_count.append(rating_count_text)
                except:
                    product_rating.append("No rating found")
                    product_rating_count.append("No rating count found")

                try:
                    link = product.select_one('a')
                    if link and 'href' in link.attrs:
                        product_link = f"https://www.myntra.com{link['href']}"
                        product_url.append(product_link)
                    else:
                        product_url.append("No URL found")
                except:
                    product_url.append("No URL found")

            # Create DataFrame from collected data
            df = pd.DataFrame({
                "Product Title": product_title,
                "Product MRP": product_mrp,
                "Discounted Price": product_discounted_price,
                "Product Image URL": product_img,
                "Product URL": product_url,
                "Product Rating": product_rating,
                "Rating Count": product_rating_count,
            })

            # Clean data: remove rows where any of the important columns have "No * found"
            df_cleaned = df[
                (df['Product Title'] != 'No title found') & 
                (df['Product MRP'] != 'No MRP found') & 
                (df['Discounted Price'] != 'No discounted price found') & 
                (df['Product Rating'] != 'No rating found') & 
                (df['Rating Count'] != 'No rating count found') & 
                (df['Product Image URL'] != 'No image found') & 
                (df['Product URL'] != 'No URL found')
            ]

            # Remove duplicate rows
            df_cleaned = df_cleaned.drop_duplicates()

            # Append new cleaned data to existing data
            combined_data = existing_data_dict + df_cleaned.to_dict(orient='records')
            df_combined = pd.DataFrame(combined_data)

            df_combined = df_combined.drop_duplicates()
            # Print progress
            print(f"Scraped {len(combined_data)} clean products from page {page_num}. Total scraped: {len(product_title)}")

            if len(df_combined) >= data_number:
                break

            page_num += 1

        if len(df_combined) >= data_number:
            break
        
        # If not enough data, retry by navigating to the next item or resetting the product lists
        print(f"Insufficient clean data ({len(combined_data)} products) for item '{item_to_scrape}'. Retrieving more data...")
    
    # Save combined data to CSV
    if len(product_title) >= data_number:
        df_sorted = df_combined.sort_values(by=['Discounted Price', 'Product Rating'], ascending=[True, False])
        
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        
        df_sorted.to_csv(output_path, index=False)
        print(f"Saved {len(df_sorted)} products' clean data to CSV file.")
    else:
        print(f"Could only scrape {len(df_cleaned)} clean products, which is less than the required {data_number}. Scraping more to meet the requirement.")
        # Optionally, save incomplete data
        df_combined.to_csv(os.path.join(output_directory, file_name + "_incomplete.csv"), index=False)

    driver.quit()
    print("Scraping completed")

# Example usage
# myntra_scraper("men-shirts", 400, "scraped_data")
