import requests
from collections import defaultdict

def message_counter(data: dict) -> dict:
    counter = defaultdict(int)
    def rec_f(data):
        if 'username' in data:
            counter[data['username']] = counter[data['username']] + 1
        if data['comments']:
            for msg in data['comments']:
                rec_f(msg)
    rec_f(data)
    sorted_res = sorted(counter.items(), key=lambda x: (-x[1], x[0]))
    return dict(sorted_res)

base_url = 'https://parsinger.ru/3.4/3/dialog.json'

try:
    response = requests.get(base_url)
    if response.ok:
        data = response.json()
        print(message_counter(data))
    else:
        print(f'Некорректный запрос, код ошибки {response.status_code}')
except requests.exceptions.JSONDecodeError as E:
    print(f'Произошла ошибка JSON: {E}')

