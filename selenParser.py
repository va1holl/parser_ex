import re
from selenium.common.exceptions import NoSuchElementException
from save_to_excel import save_to_excel
from selenium import webdriver
from selenium.webdriver.common.by import By





def get_info(url):
    driver = webdriver.Chrome()
    driver.get(url)
    products = {}

    try:
        products['product'] = driver.find_element(By.XPATH, '//h1').text
    except (AttributeError, NoSuchElementException, TypeError):
        products['product'] = None

    try:
        products['color'] = driver.find_element(By.XPATH, '//rz-var-parameter-option[1]/div/p/span[2]').text
    except (AttributeError, NoSuchElementException, TypeError):
        products['color'] = None

    try:
        products['memory_capacity'] = driver.find_element(By.XPATH, '//rz-var-parameter-option[2]/div/p/span[2]').text
    except (AttributeError, NoSuchElementException, TypeError):
        products['memory_capacity'] = None

    try:
        products['seller'] = driver.find_element(By.XPATH, '//span[@class="text-inline d-block"]').text
    except (AttributeError, NoSuchElementException, TypeError, ):
        products['seller'] = None

    try:
        products['regular_price'] = (driver.find_element(By.XPATH,
                                                         '//p[@class="product-price__small"]')
                                     .text.replace('\xa0', '').strip())
    except (AttributeError, NoSuchElementException, TypeError):
        products['regular_price'] = None

    try:
        products['discounted_price'] = (driver.find_element(By.XPATH,
                                                            '//p[@class="product-price__big text-2xl bold leading-none product-price__big-color-red"]')
                                        .text.replace('\xa0', '').strip())
    except (AttributeError, NoSuchElementException, TypeError):
        products['discounted_price'] = None

    try:
        spans = driver.find_elements(By.XPATH,
                                    '//span[contains(@class, "ms-auto") and contains(@class, "color-black-60")]')
        for span in spans:
            if "Код" in span.text:
                products['product_code'] = re.findall(r'\d+', span.text.strip())[0]
                break
        else:
            products['product_code'] = None
    except (AttributeError, NoSuchElementException, TypeError):
        products['product_code'] = None

    try:
        elements = driver.find_elements(By.XPATH,
                                    '//a[contains(@href, "/comments") and contains(text(), "відгуки")]')
        for a in elements:
            if 'відгуки' in a.text:
                products['number_of_reviews'] = re.findall(r'\d+', a.text)[0]
                break
    except (AttributeError, NoSuchElementException, TypeError):
        products['number_of_reviews'] = None

    try:
        template_dict = {}

        items = driver.find_elements(By.CSS_SELECTOR, 'dl.list div.item')
        for item in items:
            label = item.find_element(By.CSS_SELECTOR, 'dt.label span').text.strip()
            value= item.find_element(By.CSS_SELECTOR, 'dd.value a').text.strip()
            template_dict[label] = value

        products.update(template_dict)

    except (AttributeError, NoSuchElementException, TypeError):
        pass


    try:
        image_elements  = driver.find_elements(By.XPATH, '//app-slider[contains(@class, "preview-slider")]'
                                                        '//img[contains(@class, "thumbnail-button__picture")]')
        products['images'] = [img.get_attribute("src").replace("medium", "big") for img in image_elements]

    except (AttributeError, NoSuchElementException, TypeError):
        products['images'] = None


    driver.quit()
    return products



iphone = 'https://rozetka.com.ua/ua/apple-iphone-15-128gb-black/p395460480/'
products = get_info(iphone)
print(products)
save_to_excel(products, output_path='result_selenium.xlsx')