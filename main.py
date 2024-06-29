import asyncio

import aiofiles
import aiohttp
import pymorphy2
from anyio import create_task_group

import adapters.inosmi_ru as inosmi
import text_tools


TEST_ARCTICLES = ['https://inosmi.ru/20240628/drevnie-lyudi-269349491.html',
                  'https://inosmi.ru/20240629/kulisy-269369858.html',
                  'https://inosmi.ru/20240629/assanzh-269370889.html',
                  'https://inosmi.ru/20240629/evropa-269369358.html',
                  'https://inosmi.ru/20240629/top-10-269368880.html',
                  'https://inosmi.ru/20240629/byudzhet-269368449.html', ]


async def read_words_from_file(file_path):
    async with aiofiles.open(file_path, mode='rb') as word_file:
        words = []
        async for line in word_file:
            # queues['messages_queue'].put_nowait(line.decode('cp1251').strip())
            words.append(line.decode('utf8').strip())
    return words


async def fetch(session, url):
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()


async def process_article(article, articles_stat):
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, article)
        clean_plaintext = inosmi.sanitize(html, plaintext=True)

        morph = pymorphy2.MorphAnalyzer()
        article_words = text_tools.split_by_words(morph, clean_plaintext)

        charged_words = await read_words_from_file('./negative_words.txt')
        rating = text_tools.calculate_jaundice_rate(article_words, charged_words)

        articles_stat[article] = rating, len(article_words)


async def main():
    articles_stat = {}
    async with create_task_group() as tg:
        for article in TEST_ARCTICLES:
            tg.start_soon(process_article, article, articles_stat)

    for article, stats in articles_stat.items():
        print(f'URL: {article:}')
        rating, words = stats
        print(f'Рейтинг: {rating}')
        print(f'Слов в статье: {words}\n')


if __name__ == '__main__':
    asyncio.run(main())
