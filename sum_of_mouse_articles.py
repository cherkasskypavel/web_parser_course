from bs4 import BeautifulSoup
import requests


def get_articul(html: str) -> int: ##   получаем артикул со страницы товара
    soup = BeautifulSoup(html, 'html.parser')
    articul = soup.select_one('p.article').text
    return int(articul.split()[1])


def get_mouses_refs(html: str) -> list:             ##  получаем со страницы с товарами список относительных ссылок
    soup = BeautifulSoup(html, 'html.parser')       ##  на страницу продукта, где продукт - мышь
    mouses = [
        dev for dev in soup.select('div.item') if 'Мышь' in dev.select('.item .description li')[1].text
    ]
    return [mouse.select_one('a.name_item')['href'] for mouse in mouses]


def main():                                                                 ##  проходим все 4 страницы магазина,
    base_url = 'https://parsinger.ru/html/'                                 ##  получаем ссылки на страницы мышей,
    first_page_url = 'https://parsinger.ru/html/index3_page_1.html'         ##  переходим на эти страницы,
    articul_sum = 0                                                             ##  вытаскиваем артикул и суммируем
                                                                            ##  в переменную articul_sum, выводим
    with requests.Session() as S:
        first_page = S.get(first_page_url)
        first_page_soup = BeautifulSoup(first_page.text, 'html.parser')
        pages_hrefs = [a['href'] for a in first_page_soup.select('body :nth-child(1 of .pagen) a')]
        for href in pages_hrefs:
            full_url = f'{base_url}{href}'
            page = S.get(full_url)
            page.encoding = 'utf-8'
            mouses_on_page = get_mouses_refs(page.text)
            for mouse in mouses_on_page:
                response = S.get(f'{base_url}{mouse}')
                response.encoding = 'utf-8'
                articul_sum += get_articul(response.text)
    print(articul_sum)

if __name__ == '__main__':
    main()
