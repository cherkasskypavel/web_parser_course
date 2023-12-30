import os
import requests
from time import perf_counter
import asyncio
import aiohttp
import aiofiles
from bs4 import BeautifulSoup


URL = 'https://parsinger.ru/asyncio/aiofile/3/index.html'
BASE_URL = 'https://parsinger.ru/asyncio/aiofile/3/'


class Parser:


    def __init__(self, url, base_url):
        self.URL = url
        self.BASE_URL = base_url
        self.HANDLED_IMAGES = []


    def get_soup(self, url):
        print(f'Выполняется get_soup')
        with requests.get(url) as response:
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup


    def get_url_pages(self, soup):
        print(f'Выполняется get_url_pages')
        return (f'{BASE_URL}{a["href"]}' for a in soup.select('div.item_card a'))


    async def get_img_pages(self, session, url_pages):
          print(f'Выполняется get_img_pages')
          img_pages = []
          for url in url_pages:
              async with session.get(url) as response:
                  soup = BeautifulSoup(await response.text(), 'html.parser')
                  [
                      img_pages.append(f'{BASE_URL}depth2/{a["href"]}') for a in soup.select('div.item_card a')
                  ]
          await self.get_images_from_pages(session, img_pages)


    async def download_image(self, session, image_url):
        print(f'Выполняется download_image')
        name = image_url.split('/')[-1]
        if name not in self.HANDLED_IMAGES:
            async with aiofiles.open(f'images_3/{name}', 'wb') as file:
                async with session.get(image_url) as response:
                    async for chunk in response.content.iter_chunked(1024):
                        await file.write(chunk)
            self.HANDLED_IMAGES.append(name)


    async def get_images_from_pages(self, session, img_pages):
        print(f'Выполняется get_images_from_pages  ')
        for page in img_pages:
                async with session.get(page) as response:
                    soup = BeautifulSoup(await response.text(), 'html.parser')
                    for img in soup.select('img.picture'):
                        await self.download_image(session, img['src'])


    async def async_main(self, pages):
        print(f'Выполняется main')
        async with aiohttp.ClientSession() as session:
              await self.get_img_pages(session, pages)


    def __call__(self):
        print('Начало...')
        start = perf_counter()
        soup = self.get_soup(self.URL)
        pages = self.get_url_pages(soup)
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(self.async_main(pages))
        print(f'Время выполнения: {perf_counter() - start}')


parser1 = Parser(URL, BASE_URL)
parser1()

def get_folder_size(filepath, size=0):
    for root, dirs, files in os.walk(filepath):
        for f in files:
            size += os.path.getsize(os.path.join(root, f))
    return size

print(get_folder_size('images_3/'))