# Фильтр желтушных новостей

[TODO. Опишите проект, схему работы]

Пока поддерживается только один новостной сайт - [ИНОСМИ.РУ](https://inosmi.ru/). Для него разработан специальный адаптер, умеющий выделять текст статьи на фоне остальной HTML разметки. Для других новостных сайтов потребуются новые адаптеры, все они будут находиться в каталоге `adapters`. Туда же помещен код для сайта ИНОСМИ.РУ: `adapters/inosmi_ru.py`.

В перспективе можно создать универсальный адаптер, подходящий для всех сайтов, но его разработка будет сложной и потребует дополнительных времени и сил.

## Как установить

Вам понадобится Python версии 3.7 или старше. Для установки пакетов рекомендуется создать виртуальное окружение.

Первым шагом установите пакеты:

```python3
pip install -r requirements.txt
```

## Как запустить

```python3
python server.py
```

## Как использовать

Выполните запрос к серверу, в параметрах запроса передайте список url со статьями (не больше 10 адресов)

Пример запроса:

```http
http://127.0.0.1:8080/?urls=https://inosmi.ru/20240628/drevnie-lyudi-269349491.html,https://inosmi.ru/20240629/kulisy-269369858.html
```

Пример ответа:

```json
[
  {
    "status": "OK",
    "url": "https://inosmi.ru/20240629/kulisy-269369858.html",
    "score": 0.35,
    "words_count": 854
  },
  {
    "status": "OK",
    "url": "https://inosmi.ru/20240628/drevnie-lyudi-269349491.html",
    "score": 0.11,
    "words_count": 936
  }
]
```

## Как запустить тесты

Для тестирования используется [pytest](https://docs.pytest.org/en/latest/), тестами покрыты фрагменты кода сложные в отладке: `urls_handler.py`, `text_tools.py` и адаптеры. Команды для запуска тестов:

```sh
python -m pytest adapters/inosmi_ru.py
```

```sh
python -m pytest text_tools.py
```

```sh
python -m pytest urls_handler.py
```

## Цели проекта

Код написан в учебных целях. Это урок из курса по веб-разработке — [Девман](https://dvmn.org).
