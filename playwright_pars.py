from playwright.sync_api import sync_playwright, TimeoutError
import re
from save_to_excel import save_to_excel


def find_product(page):
    url = 'https://rozetka.com.ua/'
    page.goto(url)

    page.type('input[name="search"]', "Apple iPhone 15 128GB Black", delay=100)
    page.locator('button:has-text("Знайти")').click()
    page.wait_for_selector("//div[@class='goods-tile__content']")

    products = page.locator('div.goods-tile')
    count = products.count()

    for i in range(count):
        prod = products.nth(i)
        availability = prod.locator('.goods-tile__availability--available')

        if availability.count() > 0:
            title = prod.locator('.goods-tile__title')

            title.click()

            page.wait_for_selector('//html/body/rz-app-root/div/div[1]/rz-product/div/rz-product-tab-main/div/div[1]/div[2]/div/rz-product-main-info/div/div[1]/rz-title-block/div/div[2]/a/text()', timeout=15000)

            get_info(page)

            break


def get_info(page):
    products = {}

    try:
        products['product'] = page.query_selector('//h1').text_content()
    except (AttributeError, TypeError, TimeoutError):
        products['product'] = None

    try:
        products['color'] = page.query_selector('//rz-var-parameter-option[1]/div/p/span[2]').text_content()
    except (AttributeError, TimeoutError, TypeError):
        products['color'] = None

    try:
        products['memory_capacity'] = page.query_selector('//rz-var-parameter-option[2]/div/p/span[2]'
                                                          ).text_content()
    except (AttributeError, TimeoutError, TypeError):
        products['memory_capacity'] = None

    try:
        products['seller'] = page.query_selector('//span[@class="text-inline d-block"]').text_content()
    except (AttributeError, TimeoutError, TypeError,):
        products['seller'] = None

    try:
        products['regular_price'] = (page.query_selector('//p[@class="product-price__small"]')
                                     .text_content().replace('\xa0', '').strip())
    except (AttributeError, TimeoutError, TypeError):
        products['regular_price'] = None

    try:
        products['discounted_price'] = (page.query_selector(
            '//p[@class="product-price__big text-2xl bold leading-none product-price__big-color-red"]')
                                        .text_content().replace('\xa0', '').strip())
    except (AttributeError, TimeoutError, TypeError):
        products['discounted_price'] = None

    try:
        spans = page.query_selector_all(
            '//span[contains(@class, "ms-auto") and contains(@class, "color-black-60")]')
        for span in spans:
            if "Код" in span.text_content():
                products['product_code'] = re.findall(r'\d+', span.text_content().strip())[0]
                break
        else:
            products['product_code'] = None
    except (AttributeError, TimeoutError, TypeError):
        products['product_code'] = None

    try:
        elements = page.query_selector_all(
            '//a[contains(@href, "/comments") and contains(text(), "відгуки")]')
        for a in elements:
            if 'відгуки' in a.text_content():
                products['number_of_reviews'] = re.findall(r'\d+', a.text_content())[0]
                break
    except (AttributeError, TimeoutError, TypeError, IndexError):
        products['number_of_reviews'] = None

    try:
        template_dict = {}

        items = page.query_selector_all('dl.list div.item')
        for item in items:
            label = item.query_selector('dt.label span').text_content().strip()
            value = item.query_selector('dd.value a').text_content().strip()
            template_dict[label] = value

        products.update(template_dict)

    except (AttributeError, TimeoutError, TypeError):
        pass

    try:
        image_elements = page.query_selector_all('//app-slider[contains(@class, "preview-slider")]'
                                                 '//img[contains(@class, "thumbnail-button__picture")]')
        products['images'] = [img.get_attribute("src").replace("medium", "big") for img in image_elements]

    except (AttributeError, TimeoutError, TypeError):
        products['images'] = None

    print(products)
    return products


def main():
    with (sync_playwright() as p):
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        find_product(page)

        browser.close()

main()
#print(products_list)
#save_to_excel(products_list, output_path='playwright_pars.xlsx')
