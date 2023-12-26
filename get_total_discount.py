import asyncio
import aiohttp
from aiohttp_retry import RetryClient, ExponentialRetry
from aiohttp_socks import ChainProxyConnector, ProxyConnector, ProxyType, ProxyError, ProxyConnectionError
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests


INIT_URL = 'https://parsinger.ru/html/index1_page_1.html'
DOMAIN = 'https://parsinger.ru/html/'


proxies = []
category_list = []
page_list = []
price_sum = 0


def get_soup(url):
    response = requests.get(url)
    return BeautifulSoup(response.text, 'html.parser')


def get_categories(soup: BeautifulSoup) -> None:
    for a in soup.select('div.nav_menu a'):
        category_list.append(f'{DOMAIN}{a["href"]}')


def get_pages(category_lst) -> None:
    for url in category_lst:
        for a in get_soup(url).select_one('div.pagen').select('a'):
            page_list.append(f'{DOMAIN}{a["href"]}')


async def get_data(session, page_url) -> None:
    global price_sum
    retry_parameters = ExponentialRetry(attempts=6)
    retry_client = RetryClient(session, retry_options=retry_parameters, raise_for_status=False)
    try:
        async with retry_client.get(page_url) as retry_response:
            if retry_response.ok:
                response = await retry_response.text()
                soup = BeautifulSoup(response, 'html.parser')
                for div in soup.select('div.item'):
                    href = div.select_one('a')['href']
                    async with session.get(f'{DOMAIN}{href}') as response2:
                        soup2 = BeautifulSoup(await response2.text(), 'html.parser')
                        price = soup2.select_one('#price').text.split()[0]
                        old_price = soup2.select_one('#old_price').text.split()[0]
                        amount = soup2.select_one('#in_stock').text.split(': ')[-1]
                        discount = int(old_price) - int(price)
                        price_sum += discount * int(amount)
    except (ProxyError, ProxyConnectionError) as e:
        print(e)


async def main():
    ua = UserAgent()
    fake_ua = {'user-agent': ua.random}
    # connector = ChainProxyConnector.from_urls(proxies)
    # proxy = 'http://20.205.61.143:80'
    # connector = ProxyConnector().from_url('socks5://184.185.2.12:4145')

    async with aiohttp.ClientSession(headers=fake_ua) as session:
        tasks = []
        for url in page_list:
            task = asyncio.create_task(get_data(session, url))
            tasks.append(task)

        await asyncio.gather(*tasks)


if __name__ == '__main__':
    with open('good_proxies.txt', encoding='utf-8') as file:
        for proxy in file.readlines():
            proxies.append(proxy.rstrip())

    soup = get_soup(INIT_URL)
    get_categories(get_soup(INIT_URL))
    get_pages(category_list)

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
print(price_sum)
