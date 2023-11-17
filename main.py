import requests
from fake_useragent import UserAgent
from os import path

url = 'https://parsinger.ru/video_downloads/videoplayback.mp4'
ua = UserAgent()
ua_header = {'useragent': ua.random}
try:
    video_download = requests.get(url, headers=ua_header, stream=True)
    if video_download.status_code == 200:
        with open('video.mp4', 'wb') as video_file:
            try:
                for piece in video_download.iter_content(chunk_size=100000):
                    video_file.write(piece)
                file_size = round(path.getsize(video_file.name) / 1024 / 1024, 2)
                print(f'Cкачивание и запись видео в файл прошло успешно, файл весит {file_size} MB')
            except Exception as err:
                print('Произошла ошибка в процессе записи видео в файл')
    else:
        print(f'Некорректный запрос, код ошибки: {video_download.status_code}')
except Exception as e:
    print(f'Произошла ошибка на стадии запроса: {e}')
