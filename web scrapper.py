from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import traceback

def create_driver(headless: bool = False):
    """Create Chrome WebDriver using webdriver-manager (no hard-coded path)."""
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-allow-origins=*")
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def scrape_imdb_top_250(save_path: str = "IMDb_Top_250.xlsx", headless: bool = False):
    driver = create_driver(headless=headless)
    try:
        print("Opening IMDb Top 250 page...")
        driver.get("https://www.imdb.com/chart/top")

        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tbody.lister-list tr"))
        )
        time.sleep(0.5)

        rows = driver.find_elements(By.CSS_SELECTOR, "tbody.lister-list tr")
        print(f"Found {len(rows)} rows")

        data = []
        for idx, row in enumerate(rows, start=1):
            if idx > 250:
                break
            try:
                title = row.find_element(By.CSS_SELECTOR, "td.titleColumn a").text.strip()
                year = row.find_element(By.CSS_SELECTOR, "td.titleColumn span.secondaryInfo").text.strip("()")
                rating = row.find_element(By.CSS_SELECTOR, "td.imdbRating strong").text.strip()

                data.append({
                    "Rank": idx,
                    "Title": title,
                    "Year": year,
                    "IMDb Rating": rating
                })
            except Exception:
                continue

        if data:
            pd.DataFrame(data).to_excel(save_path, index=False)
            print(f"✅ Saved {len(data)} movies to {save_path}")
        else:
            print("⚠ No data found — page layout or selectors might have changed.")
    except Exception:
        print("Error during scraping:")
        traceback.print_exc()
    finally:
        try:
            driver.quit()
        except Exception:
            pass

if __name__ == "__main__":
    scrape_imdb_top_250(save_path="IMDb_Top_250.xlsx", headless=False)
