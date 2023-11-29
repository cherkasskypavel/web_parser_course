from bs4 import BeautifulSoup
import csv
import lxml
import requests


BASE_URL = 'https://parsinger.ru/html/'
INIT_PAGE_URL = 'https://parsinger.ru/html/index1_page_1.html'
FILE_NAME = 'ALL.csv'


def get_categories(html: str) -> list: ##   вернет список ссылок
    soup = BeautifulSoup(html, 'html.parser')
    return [f'{BASE_URL}{a["href"]}' for a in soup.select('.nav_menu a')]

def get_category_products(start_url: str, session: requests.Session) -> list:  ##  вернет список всех категорий для последующей записи в файл
    res_list = []
    response = session.get(start_url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'lxml')
    page_list = [f'{BASE_URL}{a["href"]}' for a in soup.select(':nth-child(1 of .pagen) a')]
    for page in page_list:
        current_response = session.get(page)
        current_response.encoding = 'utf-8'
        for name, description, price in get_products_from_page(current_response.text):
            row = [name, *description, price]
            res_list.append(row)
    return res_list

def get_products_from_page(html: str) -> zip:
    soup = BeautifulSoup(html)
    names = [a.text for a in soup.select('.item .name_item')]
    descriptions = [[li.text.split(': ')[1] for li in div.select('.description li')] for div in soup.select('.item')]
    prices = [p.text for p in soup.select('.item .price')]
    return zip(names, descriptions, prices)

def main():
    with requests.session() as S:
        response = S.get(INIT_PAGE_URL)
        response.encoding = 'utf-8'
        with open(FILE_NAME, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file, delimiter=';')
            try:
                for category in get_categories(response.text):
                    writer.writerows(get_category_products(category, S))
            except Exception as err:
                print(f'Произошла ошибка при записи файла: {err}')
        print('УСПЕХ')

main()