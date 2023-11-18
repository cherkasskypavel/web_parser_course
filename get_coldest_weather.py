import requests

def get_coldest_date(source_json, city=''):
    city_data = []
    for record in source_json:
        print(type(record))
        if record['Город'] == city or not city:
            city_data.append((record['Дата'], record['Температура воздуха']))

    return min(city_data, key=lambda x: int(x[1].strip('°C')))[0]

base_url = 'https://parsinger.ru/3.4/1/json_weather.json'

try:
    response = requests.get(base_url)
    if not response.ok:
        print(f'Проблемы с запросом, код ошибки: {response.status_code}')
    else:
        source_json = response.json()
        print(source_json)
        print(get_coldest_date(source_json)) #  по необходимости подставить город вторым аргументов в функцию
except requests.exceptions.JSONDecodeError as j_err:
    print(f'Произошла ошибка при десериализации JSON: {j_err}')
