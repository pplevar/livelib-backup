# Утилита для сохранения профилей книжного портала Livelib.ru

Сохраняет список книг (прочитанные, желаемые и проч.), а также список цитат указанного пользователя.

Не требует авторизации.

Необходимо установить зависимости:
```
pip3 install requirements.txt  # for Linux
py -m pip install requirements.txt  # for Windows
```

После чего следует запустить скрипт `export.py`, где `username` — это ваше имя пользователя, которое вы берете из ссылки на ваш личный кабинет вида https://www.livelib.ru/reader/username
```
python3 export.py username  # for Linux
python export.py username  # for Windows
```
