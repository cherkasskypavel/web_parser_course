import requests
from time import perf_counter
import asyncio
import aiohttp
from bs4 import BeautifulSoup


URL = 'https://parsinger.ru/asyncio/create_soup/1/index.html'
BASE_URL = 'https://parsinger.ru/asyncio/create_soup/1/'
HREF_LIST = []
RESULT = 0


def get_hrefs(url) -> None:

    response = requests.get(url)
    if response.ok:
        soup = BeautifulSoup(response.text, 'html.parser')
        for a in soup.select('div.item_card a'):
            HREF_LIST.append(f'{BASE_URL}{a["href"]}')


async def get_secret_code(session, url) -> None:
    global RESULT
    async with session.get(url) as response:
        resp = await response.text()
        soup = BeautifulSoup(resp, 'html.parser')
        try:
            result = soup.select_one('p.text').text
            RESULT += int(result)
        except AttributeError:
            pass


async def main():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for href in HREF_LIST:
            task = asyncio.create_task(get_secret_code(session, href))
            tasks.append(task)
        await asyncio.gather(*tasks)

get_hrefs(URL)

start = perf_counter()
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main())
end = perf_counter() - start
print(f'Время выполнения асинхронной проверки страниц: {end} сек.')

print(RESULT)
