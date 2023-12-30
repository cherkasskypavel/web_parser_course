import os
import time

import asyncio
import aiohttp
import aiofiles
from bs4 import BeautifulSoup


START_URL = 'https://parsinger.ru/asyncio/aiofile/3/index.html'
D2_SCHEME = 'https://parsinger.ru/asyncio/aiofile/3/depth2/'
D1_SCHEME = 'https://parsinger.ru/asyncio/aiofile/3/'
HANDLED_IMAGE_URLS = set()


async def get_img(session, semaphore, link):  #   работаем с множеством HANDLED_IMAGE_URLS
    async with semaphore:
        name = link.split('/')[-1]
        async with aiofiles.open(f'images_3/{name}', 'wb') as file:
            async with session.get(link) as response:
                async for chunk in response.content.iter_chunked(1024):
                    await file.write(chunk)
        print(f'    Файл {name} скачaн')


async def handle_image_urls(session, lvl_2_url):
    async with session.get(lvl_2_url) as response:
        soup = BeautifulSoup(await response.text(), 'html.parser')
        for img in soup.select('div.item_card img'):
            HANDLED_IMAGE_URLS.add(img['src'])


async def get_lvl_2_urls(session, lvl_1_url):
    async with session.get(lvl_1_url) as response:
        soup = BeautifulSoup(await response.text(), 'html.parser')
        for a in soup.select('div.item_card a'):
            lvl_2_url = f'{D2_SCHEME}{a["href"]}'
            await handle_image_urls(session, lvl_2_url)
    print(f'Ссылки второго уровня со страницы {lvl_1_url} получены')


async def main():
    semaphore = asyncio.Semaphore(200)
    print(f'Стартуем...')
    async with aiohttp.ClientSession() as session:
        # tasks = []
        async with session.get(START_URL) as response:
            soup = BeautifulSoup(await response.text(), 'html.parser')
            lvl_1_urls = [f'{D1_SCHEME}{a["href"]}' for a in soup.select('div.item_card a')]
            for url in lvl_1_urls:
                await get_lvl_2_urls(session, url)
        # await asyncio.gather(*tasks)
        # print(f'{HANDLED_IMAGE_URLS}')
        await asyncio.gather(*[get_img(session, semaphore, link) for link in HANDLED_IMAGE_URLS])


if __name__ == '__main__':
    start = time.perf_counter()
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
    end = time.perf_counter() - start
    print(f'Скачивание выполнено успешно, время выполнения : {end}')


    def get_folder_size(filepath, size=0):
        for root, dirs, files in os.walk(filepath):
            for f in files:
                size += os.path.getsize(os.path.join(root, f))
        return size

    total_size = get_folder_size('images_3/')
    total_count = len(os.listdir('images_3/'))

    print(f'Суммарный размер изображений: {total_size}')
    print(f'Всего изображений: {total_count}')