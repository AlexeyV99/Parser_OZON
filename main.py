import datetime
import json
import os
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from functions import collect_product_info

# Наименование товара
ITEM_NAME = 'наушники hyperx'
# Количество товаров первых в рейтинге
COUNT_ITEMS = 4
# Фоновый режим работы (True - включен, False - отключен)
HEADLESS = True


def result_func(response):
    print(f"response = {response}")
    with open('PRODUCTS_DATA.json', 'w', encoding='utf-8') as file:
        json.dump(response, file, indent=4, ensure_ascii=False)


def get_product_links(item_name, driver):

    driver.implicitly_wait(5)
    driver.get(url='https://ozon.ru')
    time.sleep(5)

    try:
        find_input = driver.find_element(By.NAME, 'text')
        find_input.clear()
        find_input.send_keys(item_name)
        time.sleep(2)
        find_input.send_keys(Keys.ENTER)
    except Exception as ex:
        print(ex)

    time.sleep(2)

    current_url = f'{driver.current_url}&sorting=rating'
    driver.get(url=current_url)
    time.sleep(2)

    # page_down(driver=driver)
    # time.sleep(2)

    products_urls = []
    try:
        find_links = driver.find_elements(By.CLASS_NAME, 'tile-hover-target')
        # find_links = driver.find_element(By.CLASS_NAME, 'tile-hover-target')

        for link in find_links:
            i_link = f'{link.get_attribute("href")}'
            if i_link not in products_urls:
                products_urls.append(i_link)
            if len(products_urls) >= COUNT_ITEMS:
                break

        print('[+] Ссылки собраны')
    except Exception as ex:
        print('[!] Что-то пошло не так при сборе ссылок')

    products_urls_dict = {}
    for k, v in enumerate(products_urls):
        products_urls_dict.update({k: v})

    mk_dir()
    with open('products_urls_dict.json', 'w', encoding='utf-8') as file:
        json.dump(products_urls_dict, file, indent=4, ensure_ascii=False)
    time.sleep(2)

    print(products_urls)

    products_data = []
    for url in products_urls:
        data = collect_product_info(driver=driver, url=url)
        time.sleep(2)
        products_data.append(data)

    with open('PRODUCTS_DATA.json', 'w', encoding='utf-8') as file:
        json.dump(products_data, file, indent=4, ensure_ascii=False)


def mk_dir():

    uniq_dir_name = str(datetime.datetime.now().date()) + '_' + str(datetime.datetime.now().time()).replace(':', '.')
    uniq_dir_name = f'product_{uniq_dir_name}'

    if not os.path.isdir(uniq_dir_name):
        os.mkdir(uniq_dir_name)

    os.chdir(uniq_dir_name)


if __name__ == "__main__":

    print('[INFO] Сбор данных начался. Пожалуйста ожидайте...')

    options = uc.ChromeOptions()
    options.headless = HEADLESS
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
    options.add_argument(f"--user-agent={user_agent}")
    driver = uc.Chrome(use_subprocess=False, options=options)

    get_product_links(item_name=ITEM_NAME, driver=driver)

    driver.close()
    driver.quit()
    print('[INFO] Сбор данных окончен. Работа выполнена!')
