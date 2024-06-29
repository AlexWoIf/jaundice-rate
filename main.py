import asyncio

import aiofiles
import aiohttp
import pymorphy2

import adapters.inosmi_ru as inosmi
import text_tools


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


async def main():
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, 'https://inosmi.ru/20240628/drevnie-lyudi-269349491.html')
        clean_plaintext = inosmi.sanitize(html, plaintext=True)

        morph = pymorphy2.MorphAnalyzer()
        article_words = text_tools.split_by_words(morph, clean_plaintext)

        charged_words = await read_words_from_file('./negative_words.txt')
        raiting = text_tools.calculate_jaundice_rate(article_words, charged_words)

        print(f'Рейтинг: {raiting}\nСлов в статье: {len(article_words)}')

asyncio.run(main())
