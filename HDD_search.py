from bs4 import BeautifulSoup
import csv
import requests

'''Составляем ексель-файл со всеми HDD в магазине'''

def get_items_on_page(html: str) -> zip:
    '''
    Функция возвращает информацию для каждого товара на странице
    по вабранным полям в виде итератора

    :param html: необработанное дерево html
    :return: возвращает zip-объект для последующего итерирования
    '''
    soup = BeautifulSoup(html, 'html.parser')
    names = [a.text.strip() for a in soup.select('div.item :nth-child(2 of a)')]
    desc_lists = [[li.text.split(':')[1].strip() for li in div.select('li')] for div in soup.select('div.item .description ')]
    prices = [p.text.strip() for p in soup.select('div.item .price')]
    return zip(names, desc_lists, prices)

def update_csv(name, data: zip) -> None:
    '''
    Процедура заполнения csv-файла
    записями по товарам (только данные без заголовков)

    :param name: имя файла или путь до файла
    :param data: итератор с записями по каждому товару
    '''
    with open(name, mode='a', newline='', encoding='utf-8-sig') as file:
        try:
            writer = csv.writer(file, delimiter=';')
            for name, desc, price in data:
                row = [name, *desc, price]
                writer.writerow(row)
        except Exception as err:
            print(f'Произошла ошибка при записи файла: {err}')

filename = 'HDD_info.csv'
headers = [
    'Наименование',
    'Бренд',
    'Форм-фактор',
    'Ёмкость',
    'Объем буферной памяти',
    'Цена'
]
with open(filename, mode='w', newline='', encoding='utf-8-sig') as file:    ##  записываем заголовки
    writer = csv.writer(file, delimiter=';')
    writer.writerow(headers)

counter = 1
while 1:                                                                    ##  парсим и записываем данные в файл
    current_url = f'https://parsinger.ru/html/index4_page_{counter}.html'   ##  проходясь по всем существующим страницам категории
    response = requests.get(current_url)
    if response.ok:
        response.encoding = 'utf-8'
        update_csv(filename, get_items_on_page(response.text))
    else:
        break
    counter += 1
