import asyncio
import logging
import time
from enum import Enum
from contextlib import asynccontextmanager

import aiofiles
import aiohttp
import pymorphy2
from anyio import create_task_group
from async_timeout import timeout

import adapters.inosmi_ru as inosmi
import big_text
import text_tools
from adapters.exceptions import ArticleNotFound


TEST_ARCTICLES = ['https://inosmi.ru/20240628/drevnie-lyudi-269349491.html',
                  'https://inosmi.ru/20240629/kulisy-269369858.html',
                  'https://inosmi.ru/20240629/assanzh-269370889.html',
                  'https://inosmi.ru/20240629/evropa-269369358.html',
                  'https://inosmi.ru/20240629/top-10-269368880.html',
                  'https://inosmi.ru/20240629/byudzhet-269368449.html',
                  'https://inosmi.ru/not/exist.html',
                  'https://lenta.ru/brief/2021/08/26/afg_terror/',
                  'big_text', ]
TIMEOUT = 7


class ProcessingStatus(Enum):
    OK = 'OK'
    FETCH_ERROR = 'FETCH_ERROR'
    PARSING_ERROR = 'PARSING_ERROR'
    TIMEOUT = 'TIMEOUT'


async def read_words_from_file(file_path):
    async with aiofiles.open(file_path, mode='rb') as word_file:
        words = []
        async for line in word_file:
            words.append(line.decode('utf8').strip())
    return words


async def fetch(session, url):
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()


@asynccontextmanager
async def use_timer(article, articles_stat):
    start_time = time.monotonic()
    try:
        yield start_time
    finally:
        status, rating, word_count, duration = articles_stat.get(article,
                                                                 [None]*4)
        if duration is None:
            duration = time.monotonic() - start_time
            articles_stat[article] = status, rating, word_count, duration


async def process_article(article, articles_stat, morph):
    async with aiohttp.ClientSession() as session:
        async with use_timer(article, articles_stat) as start_time:
            try:
                async with timeout(TIMEOUT):
                    if article == 'big_text':
                        clean_plaintext = big_text.big_text
                    else:
                        html = await fetch(session, article)
                        clean_plaintext = inosmi.sanitize(html, plaintext=True)

                    article_words = await text_tools.split_by_words(
                        morph, clean_plaintext)

                    charged_words = await read_words_from_file(
                        './negative_words.txt')
                    rating = text_tools.calculate_jaundice_rate(
                        article_words, charged_words)
                    status = ProcessingStatus.OK
                    word_count = len(article_words)
                    duration = time.monotonic() - start_time
                    articles_stat[article] = \
                        status, rating, word_count, duration
            except aiohttp.ClientResponseError:
                status = ProcessingStatus.FETCH_ERROR
                articles_stat[article] = status, None, None, None
            except ArticleNotFound:
                status = ProcessingStatus.PARSING_ERROR
                articles_stat[article] = status, None, None, None
            except asyncio.TimeoutError:
                status = ProcessingStatus.TIMEOUT
                articles_stat[article] = status, None, None, None


async def main():
    logging.basicConfig(
        format='%(levelname)s:%(filename)s:[%(asctime)s] %(message)s',
        level=logging.DEBUG,
    )
    articles_stat = {}
    morph = pymorphy2.MorphAnalyzer()
    async with create_task_group() as tg:
        for article in TEST_ARCTICLES:
            tg.start_soon(process_article, article, articles_stat, morph)

    for article, stats in articles_stat.items():
        print(f'\nURL: {article:}')
        status, rating, words, duration = stats
        print(f'Статус: {status.value}')
        print(f'Рейтинг: {rating}')
        print(f'Слов в статье: {words}')
        logging.info(f'Анализ закончен за {duration} сек.')


if __name__ == '__main__':
    asyncio.run(main())
