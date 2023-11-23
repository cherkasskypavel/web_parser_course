from bs4 import BeautifulSoup
import requests

base_url = 'https://parsinger.ru/html/'                         ##  ссылка для формирования абсолютной ссылки
first_page_url = 'https://parsinger.ru/html/index1_page_1.html' ##  "инициализирующая" страница


def get_total_product_price(html: str) -> int:
    '''Получаем суммарную стоимость товара по магазину'''

    soup = BeautifulSoup(html, 'html.parser')
    stock = int(soup.select_one('#in_stock').text.split()[-1])
    price = int(soup.select_one('#price').text.split()[0])
    return stock * price


def get_product_refs(html: str) -> list:
    '''Получаем относительные ссылки на товары со страницы с товарами'''

    soup = BeautifulSoup(html, 'html.parser')
    devices = [
        dev for dev in soup.select('div.item')
    ]
    return [dev.select_one('a.name_item')['href'] for dev in devices]

def get_categories_refs(html: str) -> list:
    '''Получаем список относительных ссылок на категории товаров'''

    soup = BeautifulSoup(html, 'html.parser')
    categories_refs = [a['href'] for a in soup.select('div.nav_menu a')]
    return categories_refs

def main():
    '''
    Проходимся в цикле по категориям,
        по всем страницам категории,
            по всем товарам на странице, переходя на страницу товара
                получая общую стоимость товара по магазину
        '''
    price_sum = 0
    product_counter = 0

    with requests.Session() as S:
        first_page = S.get(first_page_url)
        first_page.encoding = 'utf-8'
        for category in get_categories_refs(first_page.text):
            category_first_page = S.get(f'{base_url}{category}')
            category_first_page.encoding = 'utf-8'
            soup = BeautifulSoup(category_first_page.text, 'html.parser')
            pages_hrefs = [a['href'] for a in soup.select('body :nth-child(1 of .pagen) a')]
            for href in pages_hrefs:
                full_url = f'{base_url}{href}'
                page = S.get(full_url)
                page.encoding = 'utf-8'
                products_on_page = get_product_refs(page.text)
                for prod in products_on_page:
                    response = S.get(f'{base_url}{prod}')
                    response.encoding = 'utf-8'
                    price_sum += get_total_product_price(response.text)
                    product_counter += 1
    print(f'Суммарная стоимость всех товаров: {price_sum}')
    print(f'Всего наименований: {product_counter}')

if __name__ == '__main__':
    main()
