from bs4 import BeautifulSoup
from requests import Response, session, RequestException
import json

INIT_URL = 'https://parsinger.ru/html/index1_page_1.html'
BASE_URL = 'https://parsinger.ru/html/'
FILE_NAME = 'ALL.json'


def get_category_tags(html: str) -> dict:
    '''
    Вернет словарь, где ключи - id категории,
    а значения - относительные ссылки на переход к категории.
    '''
    soup = BeautifulSoup(html, 'html.parser')
    return {a.select_one('div')["id"]: a['href'] for a in soup.select('.nav_menu a')}

def get_page_urls(html: str) -> list:
    '''
    Вернет список url для всех страниц категории
    '''
    soup = BeautifulSoup(html, 'html.parser')
    return [f'{BASE_URL}{a["href"]}' for a in soup.select(':nth-child(1 of .pagen) a')]

def get_product_urls_on_page(html: str) -> list:
    '''
    Вернет список URL всех товаров на текущей странице
    '''
    soup = BeautifulSoup(html, 'html.parser')
    return [f'{BASE_URL}{a["href"]}' for a in soup.select('.item .name_item')]


def get_info_from_product_page(response: Response) -> dict:
    '''
    Функция собирает всю необходимую информацию
    со страницы товара и возвращает в виде словаря.

    :param response: используем Response вместо html-структуры
    для получения URL
    :return: Словарь включает как текстовые значения,
    так и словарь (по ключу description)
    '''
    soup = BeautifulSoup(response.text, 'html.parser')
    description = {
        li['id']: li.text.split(': ')[1].strip() for li in soup.select('.description li')
    }
    return {
        'name': soup.select_one('#p_header').text.strip(),
        soup.select_one('.article')['class'][0]: soup.select_one('.article').text.split(': ')[1].strip(),
        'description': description,
        'count': soup.select_one('#in_stock').text.split(': ')[1].strip(),
        'price': soup.select_one('#price').text.strip(),
        'old_price': soup.select_one('#old_price').text.strip(),
        'link': response.url
    }


def main():
    '''
    Заходим в каждую категорию, затем на каждую страницу категории
    по URL, на каждой странице собираем URL товаров и переходим
    в каждую карточку товара, добавляя словарь с информацией
    по каждому товару в список res_json, далее записываем
    список res_json в файл FILE_NAME как json объект
    :return:
    '''
    res_json = []
    with open(FILE_NAME, mode='w', encoding='utf-8-sig') as file:
        with session() as S:
            try:
                response = S.get(INIT_URL)
                response.raise_for_status()
                response.encoding = 'utf-8'
                for category_id, category_ref in get_category_tags(response.text).items():
                    category_response = S.get(f'{BASE_URL}{category_ref}')
                    category_response.raise_for_status()
                    for page in get_page_urls(category_response.text):
                        page_response = S.get(page)
                        page_response.raise_for_status()
                        page_response.encoding = 'utf-8'
                        for product in get_product_urls_on_page(page_response.text):
                            product_response = S.get(product)
                            product_response.raise_for_status()
                            product_response.encoding = 'utf-8'
                            product_info = get_info_from_product_page(product_response)
                            res = {'categories': category_id}
                            res.update(product_info)
                            res_json.append(res)
            except RequestException as req_err:
                print(f'Произошла ошибка при соединении: {req_err}')
                return
        try:
            json.dump(res_json, file, indent=4, ensure_ascii=False)
        except json.JSONDecodeError as js_err:
            print(f'Произошла ошибка при записи файла: {js_err}')
            return
    print('SUCCESS')


if __name__ == '__main__':
    main()