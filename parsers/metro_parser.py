import time
from pathlib import Path
import json
import re

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class MetroParsing:
    def __init__(self, url):
        self.base_url = "https://online.metro-cc.ru"
        self.url = url

        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome() #options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)

    def get_html_content(self, url):
        self.driver.get(url)
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "html")))
        html_content = self.driver.page_source
        return html_content

    def set_address(self, url, address, city):
        self.driver.get(url)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "html")))
        address_element = self.wait.until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "header-address__receive-address")
            )
        )
        address_element.click()
        tab_element = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//*[@id="__layout"]/div/div/'
                    'div[7]/div[2]/div/div[1]/div/div[1]/div/div[2]/div[2]',
                )
            )
        )
        tab_element.click()
        change_element = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "#__layout > div > div > div."
                    "modal-root.modal-root--active."
                    "modal-root--active-transparent > div.fon.modal-component"
                    " > div > div.modal__content > div > div.delivery__left >"
                    " div > div.pickup-content > div.pickup-content__city "
                    "> span",
                )
            )
        )
        change_element.click()
        input_element = self.wait.until(
            EC.presence_of_element_located(
                (
                    (
                        By.CSS_SELECTOR,
                        "#__layout > div > div > div.modal-root.modal-root--"
                        "active.modal-root--active-transparent > div.fon.modal"
                        "-component > div > div"
                        ".modal__content > div > div.deli"
                        "very__left > div > div.pickup-content > div.pickup-co"
                        "ntent__city > div.fon.modal-component > div > div.mod"
                        "al__content.modal__content_pt > div > div.modal-city_"
                        "_top > div.base-input.style--popup-change-tradecenter"
                        ".has-error-icon > div > div > input",
                    )
                )
            )
        )
        input_element.clear()
        input_element.send_keys(city)
        window_element = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="__layout"]/div/div/div[7]/'
                       'div[2]/div/div[1]/div/div[1]/div/div[3]'
                       '/div[1]/div[2]/div/div[1]/div/div[2]/div')))
        window_element.click()
        address_element = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, f"//*[contains(text(), '{address}')]")))
        address_element.click()
        button_element = self.wait.until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR,
                "button.simple-button.reset-button.delivery__"
                "btn-apply.style--blue.is-full-width")))
        button_element.click()
        time.sleep(5)

    def get_all_links(self, file_name: str, address: str, city: str):
        self.set_address(self.url, address, city)
        all_links = []
        page = 1

        while True:

            page_url = f"{self.url}?page={page}&in_stock=1"
            html_content = self.get_html_content(page_url)
            soup = BeautifulSoup(html_content, "html.parser")

            link_elements = soup.find_all("a", {"data-gtm": "product-card-photo-link"})

            if len(link_elements) == 0:
                break

            for element in link_elements:
                link = element["href"]
                print(link)
                all_links.append(link)

            page += 1
        base_directory = Path(__file__).parent.parent
        print(len(all_links))
        with open(f"{base_directory}/files/{file_name}", "w") as file:
            json.dump({"links": all_links}, file, indent=4)

        return all_links

    def get_info(self, urls):

        try:
            product_info_list = []

            for url in urls:
                full_url = f"{self.base_url}{url}"
                self.driver.get(full_url)

                html = self.driver.page_source

                soup = BeautifulSoup(html, "html.parser")

                product_info = {"ссылка на продукт": full_url}

                actual_price = soup.find(class_="product-unit-prices__actual")
                if actual_price:
                    meta_element = actual_price.find("meta")
                    if meta_element:
                        value = meta_element.get("content")
                        if value:
                            product_info["актуальная цена"] = value

                product_price = soup.find(
                    "div", class_="product-unit-prices__old-wrapper"
                )
                if product_price:
                    product_price_text = product_price.get_text(strip=True)
                    product_price_value = re.findall(r"\d+", product_price_text)
                    if product_price_value:
                        product_info["старая цена"] = product_price_value[0]
                    else:
                        product_info["старая цена"] = "без промо"

                product_id = soup.find("p", class_="product-page-content__article")
                if product_id:
                    product_info["артикул"] = product_id.text.strip().split(": ")[1]

                product_name_h1 = soup.find(
                    "h1",
                    class_="product-page-content__"
                    "product-name catalog-heading heading__h2",
                )
                if product_name_h1:
                    product_name_text = product_name_h1.text.strip()
                    product_info["название"] = product_name_text

                brand = soup.find("meta", itemprop="brand")
                if brand and "content" in brand.attrs:
                    brand_value = brand["content"]
                    product_info["бренд"] = brand_value
                else:
                    product_info["бренд"] = "Нет бренда"

                product_info_list.append(product_info)
                print(product_info)
            print(len(product_info_list))
            return product_info_list

        finally:
            self.driver.quit()
