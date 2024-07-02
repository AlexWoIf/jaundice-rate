import pymorphy2
from aiohttp import web
from anyio import create_task_group

import urls_handler


MAX_URLS = 10


def prepare_response(articles_stat):
    response = []
    for url, (status, rating, words_count, _) in articles_stat.items():
        response.append({'status': status.value, 'url': url, 'score': rating,
                         'words_count': words_count})
    return response


async def handle(request, morph):
    urls_text = request.rel_url.query.get('urls')
    urls = urls_text.split(',') if urls_text else []
    if len(urls) > MAX_URLS:
        raise web.HTTPBadRequest(text='{"error": "too many urls in request, '
                                 f'should be {MAX_URLS} or less"}}',
                                 content_type="application/json")
    articles_stat = {}
    async with create_task_group() as tg:
        for article in urls:
            tg.start_soon(urls_handler.process_article, article, articles_stat, morph)
    response = prepare_response(articles_stat)
    return web.json_response(response)


if __name__ == '__main__':
    morph = pymorphy2.MorphAnalyzer()

    app = web.Application()
    app.add_routes([web.get('/', lambda request: handle(request, morph))])
    web.run_app(app)
