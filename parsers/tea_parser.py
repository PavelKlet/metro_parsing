from pathlib import Path
import json
import re

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class MetroTeaParsing:
    def __init__(self, base_url, tea_url):
        self.base_url = base_url
        self.tea_url = tea_url

    @staticmethod
    def get_html_content(url):
        response = requests.get(url)
        return response.text

    def get_all_tea_links(self):
        all_links = []
        page = 1

        while True:

            page_url = f"{self.tea_url}?page={page}&in_stock=1"
            html_content = self.get_html_content(page_url)
            soup = BeautifulSoup(html_content, "html.parser")

            link_elements = soup.find_all("a", {"data-gtm": "product-card-photo-link"})

            if len(link_elements) == 0:
                break

            for element in link_elements:
                link = element["href"]
                all_links.append(link)

            page += 1
        base_directory = Path(__file__).parent.parent
        with open(f"{base_directory}/files/links.json", "w") as file:
            json.dump({"links": all_links}, file, indent=4)

        return all_links

    def get_tea_info(self, urls):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)

        try:
            product_info_list = []

            for url in urls:
                full_url = f"{self.base_url}{url}"
                driver.get(full_url)

                html = driver.page_source

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
            return product_info_list

        finally:
            driver.quit()


parser = MetroTeaParsing(
    "https://online.metro-cc.ru",
    "https://online.metro-cc.ru/category/chaj-kofe-kakao/chay",
)
