import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc


def page_down(driver):
    driver.execute_script('''
                            const scrollStep = 200; // Размер шага прокрутки (в пикселях)
                            const scrollInterval = 100; // Интервал между шагами (в миллисекундах)

                            const scrollHeight = document.documentElement.scrollHeight;
                            let currentPosition = 0;
                            const interval = setInterval(() => {
                                window.scrollBy(0, scrollStep);
                                currentPosition += scrollStep;

                                if (currentPosition >= scrollHeight) {
                                    clearInterval(interval);
                                }
                            }, scrollInterval);
                        ''')


def collect_product_info(url):
    time.sleep(3)
    # print(url)
    options = uc.ChromeOptions()
    options.headless = True
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
    options.add_argument(f"--user-agent={user_agent}")
    options.add_argument('--ignore-certificate-errors')
    driver = uc.Chrome(use_subprocess=True, options=options, user_multi_procs=True)

    driver.get(url=url)

    time.sleep(3)
    # driver.get_screenshot_as_file(f"screenshot-2-{url.split('/')[4][-9::]}.png")
    # product_id
    product_id = driver.find_element(
        By.XPATH, '//div[contains(text(), "Артикул: ")]'
    ).text.split('Артикул: ')[1]

    page_source = str(driver.page_source)
    soup = BeautifulSoup(page_source, 'lxml')

    with open(f'product_{product_id}.html', 'w', encoding='utf-8') as file:
        file.write(page_source)

    product_name = soup.find('div', attrs={"data-widget": 'webProductHeading'}).find(
        'h1').text.strip().replace('\t', '').replace('\n', ' ')

    # product_id
    # try:
    #     product_id = soup.find('div', string=re.compile(
    #         'Артикул:')).text.split('Артикул: ')[1].strip()
    # except:
    #     product_id = None

    # product statistic
    try:
        product_statistic = soup.find(
            'div', attrs={"data-widget": 'webSingleProductScore'}).text.strip()

        if " • " in product_statistic:
            product_stars = product_statistic.split(' • ')[0].strip()
            product_reviews = product_statistic.split(' • ')[1].strip()
        else:
            product_statistic = product_statistic
    except:
        product_statistic = None
        product_stars = None
        product_reviews = None

    # product price
    try:
        ozon_card_price_element = soup.find(
            'span', string="c Ozon Картой").parent.find('div').find('span')
        product_ozon_card_price = ozon_card_price_element.text.strip(
        ) if ozon_card_price_element else ''

        price_element = soup.find(
            'span', string="без Ozon Карты").parent.parent.find('div').findAll('span')

        product_discount_price = price_element[0].text.strip(
        ) if price_element[0] else ''
        product_base_price = price_element[1].text.strip(
        ) if price_element[1] is not None else ''
    except:
        product_ozon_card_price = None
        product_discount_price = None
        product_base_price = None

    # product price
    try:
        ozon_card_price_element = soup.find(
            'span', string="c Ozon Картой").parent.find('div').find('span')
    except AttributeError:
        card_price_div = soup.find(
            'div', attrs={"data-widget": "webPrice"}).findAll('span')

        product_base_price = card_price_div[0].text.strip()
        product_discount_price = card_price_div[1].text.strip()

    product_data = (
        {
            'product_id': product_id,
            'product_name': product_name,
            'product_ozon_card_price': product_ozon_card_price,
            'product_discount_price': product_discount_price,
            'product_base_price': product_base_price,
            'product_statistic': product_statistic,
            'product_stars': product_stars,
            'product_reviews': product_reviews,
        }
    )
    print(f'[+] Собраны данные о товаре: {product_id} - {product_name}')
    driver.close()
    driver.quit()
    time.sleep(2)
    return product_data
