import requests
from time import perf_counter

total = 0
base_url = 'https://parsinger.ru/3.3/2/'
headers = {
    'connection': 'open',
}
a = perf_counter()
with requests.Session() as S:
    for i in range(1, 201):
        response = S.head(url=f'{base_url}{i}.html')
        total += response.status_code
print(f'Время выполнения: {perf_counter() - a}')
print(f'Сумма статус-кодов: {total}')
