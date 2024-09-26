import datetime
import json
import os
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from functions_multiproc import collect_product_info
import multiprocessing


# Наименование товара
ITEM_NAME = 'наушники hyperx'
# Количество товаров первых в рейтинге
COUNT_ITEMS = 4
# Фоновый режим работы (True - включен, False - отключен)
HEADLESS = True


def result_func(response):
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


    # products_data = []
    # for url in products_urls:
    #     data = collect_product_info(driver=driver, url=url)
    #     time.sleep(2)
    #     products_data.append(data)
    #
    # with open('PRODUCTS_DATA.json', 'w', encoding='utf-8') as file:
    #     json.dump(products_data, file, indent=4, ensure_ascii=False)
    return products_urls


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

    products_urls = get_product_links(item_name=ITEM_NAME, driver=driver)

    # products_urls = ['https://www.ozon.ru/product/hyperx-wired-headphones-with-microphone-3-5-mm-silvery-429745678/?asb2=_YDMXat5y4lirl3bxElMFXxYuq7mzR8bURP9BAyQqPzFzAIhnbpvNHOvoITQBYY1&avtc=1&avte=1&avts=1727340394&keywords=%D0%BD%D0%B0%D1%83%D1%88%D0%BD%D0%B8%D0%BA%D0%B8+hyperx',
    #                  'https://www.ozon.ru/product/hyperx-naushniki-provodnye-s-mikrofonom-radiokanal-3-5-mm-x2-bronza-1366506930/?asb2=rPHi2TG1NRsWp4-4dtAEokcnmn9KVW0XLJO0mGSwVEGy4WDvs_eGnQeVAtJj8lz9x791cfmmPzyxHy-S1uNmDw&avtc=1&avte=2&avts=1727340394&keywords=%D0%BD%D0%B0%D1%83%D1%88%D0%BD%D0%B8%D0%BA%D0%B8+hyperx',
    #                  'https://www.ozon.ru/product/igrovye-naushniki-hyperx-cloud-iii-black-red-1252752573/?asb2=g_Ikdsqo8MSKL7l23rJ_n0naZcMVplbvIUOcbuPF1XvaKHvh5IML62bFMVDN_XsZFn06ONnZKKHjFRGHCPT4Dw&avtc=1&avte=1&avts=1727340394&keywords=%D0%BD%D0%B0%D1%83%D1%88%D0%BD%D0%B8%D0%BA%D0%B8+hyperx',
    #                  'https://www.ozon.ru/product/igrovye-provodnye-naushniki-hyperx-cloud-alpha-s-3-5-mm-s-mikrofonom-chernye-sinie-663019803/?asb2=EB7cuyzM3o6YVBK8-dYPoIax92-pIPXOGUan3PmeBbmSHemCwTbijJY9jaoZMRSdSOPZP6lVQfcbARGP5NI-hQ&avtc=1&avte=2&avts=1727340394&keywords=%D0%BD%D0%B0%D1%83%D1%88%D0%BD%D0%B8%D0%BA%D0%B8+hyperx'
    #                  ]

    with multiprocessing.Pool(processes=4) as p:
        p.map_async(collect_product_info, products_urls, callback=result_func)
        p.close()
        p.join()

    driver.close()
    driver.quit()
    print('[INFO] Сбор данных окончен. Работа выполнена!')
