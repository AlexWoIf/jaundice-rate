import json

from aiohttp import web


async def handle(request):
    urls = request.rel_url.query.get('urls')
    text = json.dumps({'urls': urls.split(',') if urls else []}, indent=4)
    return web.Response(text=text)

app = web.Application()
app.add_routes([web.get('/', handle),
                web.get('/{name}', handle)])

if __name__ == '__main__':
    web.run_app(app)
