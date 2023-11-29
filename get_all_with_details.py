'''
Программа собирает информацию по каждому товару,
проходясь по всем страницам каждой категории
и, наконец, переходя в карточку товара,
и формирует CSV-файл FILE_NAME с полями HEADERS.
'''

from bs4 import BeautifulSoup
import csv
import lxml
from requests import RequestException, session, Session



BASE_URL = 'https://parsinger.ru/html/'                         ##  Страница начала работы программы
INIT_PAGE_URL = 'https://parsinger.ru/html/index1_page_1.html'  ##  Начальная страница
FILE_NAME = 'ALL_PRODUCTS_WITH_DETAILS.csv'
FILE_HEADERS = [
    'Наименование',
    'Артикул',
    'Бренд',
    'Модель',
    'Наличие',
    'Цена',
    'Старая цена',
    'Ссылка'
]

def get_categories(html: str) -> list:  ##   вернет список ссылок на категории
    soup = BeautifulSoup(html, 'html.parser')
    return [f'{BASE_URL}{a["href"]}' for a in soup.select('.nav_menu a')]

def get_hrefs_from_page(html: str) -> list: ##  вернет список ссылок товаров на странице
    soup = BeautifulSoup(html, 'lxml')
    return [a['href'] for a in soup.select('.name_item[href]')]

def get_info_from_product_page(html: str) -> list:  ##  вернет список информации по указанным полям
    soup = BeautifulSoup(html, 'lxml')              ##  со страницы товара, за исключением поля "Ссылка"
    name = soup.select_one('#p_header').text.strip()
    article = int(soup.select_one('.article').text.split(': ')[1])
    brand = soup.select_one('#brand').text.split(': ')[1]
    model = soup.select_one('#model').text.split(': ')[1]
    stock = int(soup.select_one('#in_stock').text.split(': ')[1])
    price = soup.select_one('#price').text
    old_price = soup.select_one('#old_price').text
    return [name, article, brand, model, stock, price, old_price]
def get_category_products(start_url: str, session: Session) -> list:
    '''
    Переходим на 1 страницу категории, получаем список страниц категории,
    проходим по страницам, получаем список относительных ссылок на товары,
    заходим в карточку каждого товара и собираем
    информацию по полям HEADERS с помощью функции get_info_from_product_page()

    :param start_url: первая страница категории;
    :param session: передаем сессию как параметр
    :return: возвращаем список списков с информацией по полям HEADERS для каждого товара
    '''
    category_list = []
    response = session.get(start_url)
    response.raise_for_status()
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'lxml')
    page_list = [f'{BASE_URL}{a["href"]}' for a in soup.select(':nth-child(1 of .pagen) a')] ## список страниц категории
    for page in page_list:
        current_page_response = session.get(page)
        current_page_response.raise_for_status()
        for href in get_hrefs_from_page(current_page_response.text):        ##  проходим по списку ссылок товаров
            prodict_url = f'{BASE_URL}{href}'                               ##  формируя URL
            current_product_response = session.get(prodict_url)
            current_product_response.raise_for_status()
            current_product_response.encoding = 'utf-8'
            category_list.append(get_info_from_product_page(current_product_response.text) + [current_product_response.url]) ## добавляем поле "Ссылка"
    return category_list

def main():
    '''
    Записывваем в файл список списков для каждой категории
    '''
    with session() as S:
        try:
            response = S.get(INIT_PAGE_URL)
            response.encoding = 'utf-8'
            with open(FILE_NAME, mode='w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow(FILE_HEADERS)
                for category in get_categories(response.text):
                    writer.writerows(get_category_products(category, S))
        except RequestException as err:
            print(f'Произошла ошибка при выбполнении запроса: {err}')
        print('УСПЕХ')

main()