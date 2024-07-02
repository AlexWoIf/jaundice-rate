import pymorphy2
from aiohttp import web
from anyio import create_task_group

import main


def prepare_response(articles_stat):
    response = []
    for url, (status, rating, words_count, duration) in articles_stat.items():
        response.append({'status': status.value, 'url': url, 'score': rating,
                         'words_count': words_count})
    return response


async def handle(request, morph):
    urls = request.rel_url.query.get('urls')
    articles_stat = {}
    async with create_task_group() as tg:
        for article in urls.split(',') if urls else []:
            tg.start_soon(main.process_article, article, articles_stat, morph)
    response = prepare_response(articles_stat)
    print(response)
    return web.json_response(response)
    # return web.json_response({'urls': urls.split(',') if urls else []})


if __name__ == '__main__':
    # logging.basicConfig(
    #     format='%(levelname)s:%(filename)s:[%(asctime)s] %(message)s',
    #     level=logging.DEBUG,
    # )
    morph = pymorphy2.MorphAnalyzer()

    app = web.Application()
    app.add_routes([web.get('/', lambda request: handle(request, morph))])
    web.run_app(app)
