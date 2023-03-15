"""
to do
"""
import csv
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    StaleElementReferenceException
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import List
from webdriver_manager.chrome import ChromeDriverManager


from .utils import (
    extract_string_from_listing,
    extract_ad_price,
    extract_kms_year
)

class Scraper():
    """
    The main class containting all the scraping logic. Contains two methods:

    - .scrape(input_url): returns a list of list of scraped data for given <input_url>
    - .scrape_to_csv(input_url, file_name): scrapes given <input_url> and writes to csv
        name as per <file_name>, stored at root dir
    """
    def _load_page_source(self, input_url: str) -> str:
        """
        load all the listings for given input_url using selenium.
        """
        service = Service(executable_path=ChromeDriverManager().install())
        chrome_options = Options()
        ua = UserAgent()
        user_agent = ua.random
        chrome_options.add_argument(f'user-agent={user_agent}')
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(input_url)
        staleness_counter = 0
        while staleness_counter <= 2:
            try:
                load_more_button = (
                    WebDriverWait(driver, 20)
                    .until(EC.visibility_of_element_located(
                        (By.XPATH, '//button[contains(@data-aut-id, "btnLoadMore")]')
                    ))
                )
                load_more_button.click()
            except (NoSuchElementException, TimeoutException):
                break
            except StaleElementReferenceException:
                staleness_counter += 1
                continue
        return driver.page_source

    def _scrape_page_source(self, page_source: str) -> List[List[str]]:
        """
        give a html page source, scrape for listing details and store
        as list of lists
        """
        soup = BeautifulSoup(page_source, 'html.parser')
        car_listings_ul = soup.find("ul", attrs={"data-aut-id": "itemsList"})
        listings = car_listings_ul.find_all("li", attrs={"data-aut-id": "itemBox"})

        data = []
        for listing in listings:
            ad_link = listing.find("a")["href"]
            ad_id = ad_link.split("-")[-1]
            ad_title = extract_string_from_listing(
                listing=listing, html_tag="span",
                html_attribute="data-aut-id", attribute_value="itemTitle"
            )
            ad_price = extract_ad_price(listing)
            kms_driven, model_year = extract_kms_year(listing)
            ad_location = extract_string_from_listing(
                listing=listing, html_tag="span",
                html_attribute="data-aut-id", attribute_value="item-location"
            )
            data.append([ad_id, ad_price, model_year, kms_driven, ad_title, ad_location, ad_link])
        
        return data

    def _write_parsed_to_csv(self, data: List[List[str]], file_name: str) -> None:
        """
        given list of lists, write it to a .csv for the given file name.
        note: file_name should not have extension
        """
        with open(f'{file_name}.csv', 'w', newline='', encoding="utf-8") as file: 
            writer = csv.writer(file)
            headers = ['Ad ID','Price','Model Year', 'KMS Driven', 'Ad Title', 'Ad Location', 'Ad Link']
            writer.writerow(headers)
            for row in data:
                writer.writerow(row)

    def scrape(self, input_url: str) -> List[List[str]]:
        """
        scrapes given <input_url> and returns a python list of list containing the data,
        this can be used to either write to a csv or generation of a pandas dataframe
        for further analysis
        """
        page_source = self._load_page_source(input_url)
        scraped_data = self._scrape_page_source(page_source)
        return scraped_data
    
    def scrape_to_csv(self, input_url: str, file_name: str) -> None:
        """
        scrapes data for given <input_url> to csv file located at root dir with
        <file_name> specified. note: file extension not required.
        """
        scraped_data = self.scrape(input_url=input_url)
        output_csv = self._write_parsed_to_csv(data=scraped_data, file_name=file_name)