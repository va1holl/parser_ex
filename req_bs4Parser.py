import re
import requests
from bs4 import BeautifulSoup
from lxml import etree
from save_to_excel import save_to_excel

url = 'https://rozetka.com.ua/ua/apple-iphone-15-128gb-black/p395460480/'
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/123.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;"
              "q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "DNT": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "no-cache",
}


def find_value_in_label(soup, label):

    label = soup.find('dt', class_='label', string=lambda text: text and label in text)
    if not label:
        return None

    value_tag = label.find_next_sibling('dd')
    if not value_tag:
        return None

    value = value_tag.find('a')
    return value.get_text(strip=True) if value else value_tag.get_text(strip=True)


def safe(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (AttributeError, IndexError, TypeError):
            return None
    return wrapper


@safe
def extract_product(dom):
    return dom.xpath('//h1')[0].text


@safe
def extract_color(dom):
    return dom.xpath('//rz-var-parameter-option[1]/div/p/span[2]')[0].text


@safe
def extract_memory(dom):
    return dom.xpath('//rz-var-parameter-option[2]/div/p/span[2]')[0].text


@safe
def extract_seller(dom):
    return dom.xpath('//span[@class="text-inline d-block"]')[0].text


@safe
def extract_regular_price(dom):
    return dom.xpath('//p[@class="product-price__small"]')[0].text.replace('\xa0', '').strip()


@safe
def extract_discounted_price(dom):
    return (
        dom.xpath(
            '//p[@class="product-price__big text-2xl bold leading-none product-price__big-color-red"]')[0]
        .text.replace('\xa0', '').strip()
    )


@safe
def extract_product_code(dom):
    raw = dom.xpath('//span[@class="ms-auto color-black-60"]')[0].text.replace('\xa0', '').strip()
    return re.findall(r'\d+', raw)[0]


@safe
def extract_reviews(dom):
    raw = dom.xpath('//button[@class="button comments-tabs__button comments-tabs__active"]')
    return re.findall(r'\d+', raw[0].text)[0]

@safe
def extract_chars(dom):
    template_dict = {}
    characters_tag = dom.find('dl', class_='list')
    items = characters_tag.find_all('div', class_='item')
    for item in items:
        label = item.find('span').text.strip()
        template_dict[f'{label}'] = find_value_in_label(characters_tag, label)

    return template_dict

def get_info(link):
    products = {}
    response = requests.get(link, headers=headers)
    print(response.status_code)
    soup = BeautifulSoup(response.text, 'html.parser')
    dom = etree.HTML(str(soup))

    products['product'] = extract_product(dom)
    products['color'] = extract_color(dom)
    products['memory_capacity'] = extract_memory(dom)
    products['seller'] = extract_seller(dom)
    products['regular_price'] = extract_regular_price(dom)
    products['discounted_price'] = extract_discounted_price(dom)
    products['product_code'] = extract_product_code(dom)
    products['number_of_reviews'] = extract_reviews(dom)
    products.update(extract_chars(soup))

    try:
        slider_tag = soup.find('app-slider', class_="preview-slider")
        image_tags = slider_tag.find_all('img', class_='thumbnail-button__picture')
        products['images'] = [img['src'].replace('medium', 'big') for img in image_tags]
    except AttributeError:
        products['images'] = None

    return products





products = get_info(url)
print(products)
save_to_excel(products)