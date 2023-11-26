from bs4 import BeautifulSoup
import csv
import requests

'''                                           В ПРОЦЕССЕ ДОРАБОТКИ                                        '''

BASE_URL = 'https://parsinger.ru/html/'
FILE_NAME = 'WATCH.csv'
HEADERS = [
    'Наименование',
    'Артикул',
    'Бренд',
    'Модель',
    'Тип',
    'Технология экрана',
    'Материал корпуса',
    'Материал браслета',
    'Размер',
    'Сайт производителя',
    'Наличие',
    'Цена',
    'Старая цена',
    'Ссылка на карточку с товаром'
]

def get_product_page_info(html: str, url: str) -> tuple:
    soup = BeautifulSoup(html, 'html.parser')
    name = soup.select_one('#p_header').text
    article = soup.select_one('.description .article').text.split()[1]
    description = [li.text.split(': ')[1] for li in soup.select('#description li')]
    stock = soup.select_one('#in_stock').text.split(':')[1].strip()
    price = soup.select_one('#price').text
    old_price = soup.select_one('#old_price').text
    return name, article, description, stock, price, old_price, url

def update_csv(file: str, data: tuple) -> None:
    try:
        with open(file, mode='a', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file, delimiter=';')
            name, article, description, stock, price, old_price, url = data
            row = article, *description, stock, price, old_price, url
            writer.writerow(row)
    except Exception as err:
        print(f'Произошла ошибка при записи файла: {err}')

def write_all_products_from_page(html: str, session: requests.Session) -> None:
    soup = BeautifulSoup(html, 'html.parser')
    hrefs = [a['href'] for a in soup.select('.item [href].name_item')]
    for href in hrefs:
        full_url = f'{BASE_URL}{href}'
        response = session.get(full_url)
        response.encoding = 'utf-8'
        update_csv(FILE_NAME, get_product_page_info(response.text, full_url))

def main():
    with open(FILE_NAME, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(HEADERS)

    with requests.Session() as S:
        counter = 1
        while 1:
            response = S.get(f'https://parsinger.ru/html/index1_page_{counter}.html')
            if response.ok:
                response.encoding = 'utf-8'
                write_all_products_from_page(response.text, S)
                print(f'Данные со страницы {counter} обработаны')
                counter += 1
            else:
                break
    print(f'\nФайл {FILE_NAME} записан')

main()