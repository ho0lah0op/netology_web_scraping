import datetime
import json
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import StaleElementReferenceException

chrome_driver_path = ChromeDriverManager().install()
browser_service = Service(executable_path=chrome_driver_path)
browser = Chrome(service=browser_service)

browser.get(
    "https://spb.hh.ru/search/vacancy?area=1&area=2&search_field=name&search_field=company_name&search_field=description&enable_snippets=true&L_save_area=true&text=python")

parsed_data = []

while True:
    try:
        vacancies = browser.find_elements(By.CLASS_NAME, "vacancy-serp-item__layout")
        for vacancy in vacancies:
            descriptions = vacancy.find_elements(By.CLASS_NAME, "bloko-text")
            description_text = ' '.join([description.text for description in descriptions])
            has_django = "Django" in description_text
            has_flask = "Flask" in description_text

            if has_django or has_flask:
                h3_tag = vacancy.find_element(By.TAG_NAME, "h3")
                a_tag = h3_tag.find_element(By.TAG_NAME, "a")
                company_info = vacancy.find_element(By.CLASS_NAME, "vacancy-serp-item-company")
                city_element = vacancy.find_element(By.CSS_SELECTOR, '[data-qa="vacancy-serp__vacancy-address"]')

                try:
                    span_tag = vacancy.find_element(By.CLASS_NAME, "bloko-header-section-2")
                    salary = span_tag.text.strip().replace('\u202f', ' ')

                except:
                    salary = None

                header = h3_tag.text
                link_absolute = a_tag.get_attribute("href")
                company_name = company_info.find_element(By.TAG_NAME, "a").text
                city_name = city_element.text.strip().split(',')[
                    0] if ',' in city_element.text.strip() else city_element.text.strip()

                parsed_data.append({
                    "header": header,
                    "link": link_absolute,
                    "salary": salary,
                    "company": company_name,
                    "city": city_name
                })

        next_button = browser.find_elements(By.CSS_SELECTOR, 'a.bloko-button[data-qa="pager-next"]')

        if not next_button:
            break

        next_button[0].click()

    except StaleElementReferenceException:
        pass

current_date = datetime.datetime.now().strftime("%d_%m_%Y")
file_name = f'vacancies_{current_date}.json'

with open(file_name, 'w', encoding='utf-8') as json_file:
    json.dump(parsed_data, json_file, ensure_ascii=False, indent=4)
    print(f"Данные успешно записаны в {file_name}")

browser.quit()
