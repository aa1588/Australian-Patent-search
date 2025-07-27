from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json


KEYWORD = "sky"

driver = webdriver.Chrome()
driver.get("https://ipsearch.ipaustralia.gov.au/patents/")
driver.maximize_window()

# find the search input field and enter the query
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "query"))).send_keys(KEYWORD)

# find the search button and click it
WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Show')]"))).click()

# wait for the results to load
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='search-results']/div/div[1]/div/table/thead/tr")))

# extract the headers from the table
headers = [th.text.strip() for th in driver.find_elements(By.XPATH, '//*[@id="search-results"]/div/div[1]/div/table/thead/tr/th')]

all_results = []
page_number = 1


while True:

    print(f"Scraping page {page_number}...")

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="search-results"]/div/div[1]/div/table/tbody/tr')))
    rows = driver.find_elements(By.XPATH, '//*[@id="search-results"]/div/div[1]/div/table/tbody/tr')

    for row in rows:
        cols = row.find_elements(By.TAG_NAME, 'td')
        result = {}

        for i in range(min(len(headers), len(cols))):
            result[headers[i]] = cols[i].text.strip()
        all_results.append(result)        

    try:
        next_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Next' and not(@aria-disabled='true')]"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
        time.sleep(0.5)
        next_button.click()

        # increment the page number
        page_number += 1
        
        time.sleep(2)  # wait for the next page to load
    except:
        print("Reached the last page or no next button available.")
        break

# save results to a file
filename = f"results_{KEYWORD}.json"

with open(filename, 'w') as f:
    json.dump(all_results, f, indent=2, ensure_ascii=False)

# close the browser
driver.quit()

# done
print(f"Scraped {len(all_results)} results across {page_number} pages.")