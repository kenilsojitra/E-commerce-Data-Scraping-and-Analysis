from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from amazoncaptcha import AmazonCaptcha
import time
from bs4 import BeautifulSoup
import os

def amazon_scraper(item_to_scrape, data_number, file_name):
    try:
        data_number = int(data_number) * 3 # To ensure we get enough clean data
    except ValueError:
        print("Error: data_number must be an integer.")
        return

    url = "https://www.amazon.com/"
    
    service = Service(executable_path="D:\\projects python django\\scraper\\home\\chromedriver.exe")
    driver = webdriver.Chrome(service=service)
    driver.get(url)

    # Handle CAPTCHA
    try:
        captcha_image = driver.find_element(By.XPATH, "//div[@class='a-row a-text-center']//img")
        if captcha_image:
            link = captcha_image.get_attribute('src')
            captcha = AmazonCaptcha.fromlink(link)
            captcha_value = AmazonCaptcha.solve(captcha)

            get_captcha = driver.find_element(By.ID, "captchacharacters")
            get_captcha.clear()
            get_captcha.send_keys(captcha_value, Keys.ENTER)
    except Exception as e:
        print("Captcha not found or error solving captcha:", e)

    # Change currency to Indian Rupees (INR)
    try:
        change_button = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='nav-tools']//a[contains(@href, 'customer-preferences')]"))
        )
        change_button.click()

        select_dropdown = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".a-dropdown-prompt"))
        )
        select_dropdown.click()
        print("Opened currency dropdown.")

        # Select Indian Rupees currency preference
        indian_rupees_radio = driver.find_element(By.ID, "INR")
        indian_rupees_radio.click()

        # Save changes
        save_changes_button = driver.find_element(By.ID, "icp-save-button")
        save_changes_button.click()

        print("Currency changed to Indian Rupees (INR).")
    except Exception as e:
        print(f"Error changing currency: {e}")

    product_title = []
    product_mrp = []
    product_discounted_price = []
    product_rating = []
    product_rating_count = []
    product_img = []
    product_url = []

    while len(product_title) < data_number:
        page_num = 1
        while len(product_title) < data_number:
            page_url = f"https://www.amazon.com/s?k={item_to_scrape}&page={page_num}"
            driver.get(page_url)
            time.sleep(3)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            products = soup.select(".s-search-results .s-result-item")
            
            if not products:
                print(f"No products found on page {page_num}. Ending scraping for item.")
                break

            for product in products:
                if len(product_title) >= data_number:
                    break

                try:
                    title_tag = product.select_one('h2 a')
                    title = title_tag.get_text(strip=True) if title_tag else "No title found"
                    product_title.append(title)
                    
                    url = "https://www.amazon.com" + title_tag['href'] if title_tag else "No URL found"
                    product_url.append(url)
                except:
                    product_title.append("No title found")
                    product_url.append("No URL found")

                try:
                    mrp = product.select_one('.a-price.a-text-price .a-offscreen')
                    product_mrp.append(mrp.get_text(strip=True) if mrp else "No MRP found")
                    
                    discounted_price = product.select_one('.a-price .a-offscreen:not(.a-text-price .a-offscreen)')
                    product_discounted_price.append(discounted_price.get_text(strip=True) if discounted_price else "No discounted price found")
                except:
                    product_mrp.append("No MRP found")
                    product_discounted_price.append("No discounted price found")

                try:
                    rating = product.select_one('.a-icon-alt')
                    product_rating.append(rating.get_text(strip=True) if rating else "No rating found")
                except:
                    product_rating.append("No rating found")

                try:
                    rating_count = product.select_one('.a-size-small .a-link-normal')
                    product_rating_count.append(rating_count.get_text(strip=True) if rating_count else "No rating count found")
                except:
                    product_rating_count.append("No rating count found")

                try:
                    image = product.select_one('.s-image')
                    product_img.append(image['src'] if image else "No image found")
                except:
                    product_img.append("No image found")

            print(f"Scraped {len(product_title)} products from page {page_num}. Total scraped: {len(product_title)}")
            if len(product_title) >= data_number:
                break

            page_num += 1

        if len(product_title) >= data_number:
            break
        
        print(f"Insufficient clean data ({len(product_title)}) for item '{item_to_scrape}'. Retrieving more data...")

    if len(product_title) > 0:
        output_directory = "csv_folder"
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        
        df = pd.DataFrame({
            "Product Title": product_title,
            "Product MRP": product_mrp,
            "Discounted Price": product_discounted_price,
            "Product Rating": product_rating,
            "Rating Count": product_rating_count,
            "Product Image URL": product_img,
            "Product URL": product_url,
        })

        df_cleaned = df[
            (df['Product Title'] != 'No title found') & 
            (df['Product MRP'] != 'No MRP found') & 
            (df['Discounted Price'] != 'No discounted price found') & 
            (df['Product Rating'] != 'No rating found') & 
            (df['Rating Count'] != 'No rating count found') & 
            (df['Product Image URL'] != 'No image found') & 
            (df['Product URL'] != 'No URL found')
        ]

        df_sorted = df_cleaned.sort_values(by=['Discounted Price', 'Product Rating'], ascending=[True, False])

        df_sorted.to_csv(os.path.join(output_directory, file_name + ".csv"), index=False)
        print(f"Saved {len(df_sorted)} products' clean data to CSV file.")
    else:
        print("No products scraped")

    driver.quit()
    print("Scraping completed")
