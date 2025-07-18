import re
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from save_to_excel import save_to_excel
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC



def find_product(driver, url):
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, 'search'))
    )

    search_input = driver.find_element(By.NAME, 'search')
    search_input.send_keys('Apple iPhone 15 128GB Black')
    search_input.send_keys(Keys.RETURN)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[@class='goods-tile__content']"))
    )

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'div.goods-tile'))
    )

    products = driver.find_elements(By.CSS_SELECTOR, 'div.goods-tile')
    print(len(products))

    for product in products:
        avail = product.find_element(By.CSS_SELECTOR, '.goods-tile__availability--available')

        title = product.find_element(By.CSS_SELECTOR, '.goods-tile__title')
        title.click()

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "text-base product-comment-rating__text")]'))
        )

        return get_info(driver)


def get_info(driver):

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
                                     .text.replace('\xa0', '').replace(' ', '').replace('₴', '').strip())
    except (AttributeError, NoSuchElementException, TypeError):
        products['regular_price'] = None

    try:
        products['discounted_price'] = (driver.find_element(By.XPATH,
                                                            '//p[@class="product-price__big text-2xl bold leading-none product-price__big-color-red"]')
                                        .text.replace('\xa0', '').replace(' ', '').replace('₴', '').strip())
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

def main():
    driver = webdriver.Chrome()
    url = 'https://rozetka.com.ua/ '
    products = find_product(driver, url)
    print(products)
    save_to_excel(products, output_path='result_selenium.xlsx')

main()