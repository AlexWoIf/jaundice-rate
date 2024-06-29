import asyncio

import aiohttp
import pymorphy2

import adapters.inosmi_ru as inosmi
import text_tools

async def fetch(session, url):
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()


async def main():
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, 'https://inosmi.ru/20240628/drevnie-lyudi-269349491.html')
        clean_plaintext = inosmi.sanitize(html, plaintext=True)
        # print(clean_plaintext)

        morph = pymorphy2.MorphAnalyzer()
        article_words = text_tools.split_by_words(morph, clean_plaintext)
        charged_words = ['срочно', 'весьма', 'эксклюзивный']
        raiting = text_tools.calculate_jaundice_rate(article_words, charged_words)

        words_raiting = {}
        for word in article_words:
            words_raiting[word] = words_raiting.get(word, 0) + 1
        # sorted_raiting = {key: value for key, value in 
        #                   sorted(words_raiting.items(),
        #                          key=lambda item: item[1])}
        for word in charged_words:
            print(f'{word}: {words_raiting.get(word, 0)}')
        print(f'Рейтинг: {raiting}\nСлов в статье: {len(article_words)}')

asyncio.run(main())
