"""A simple URL shortener using Werkzeug and redis."""
import math
import os
from urllib.parse import urlsplit

from jinja2 import Environment, FileSystemLoader
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.middleware.shared_data import SharedDataMiddleware
from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Request, Response

from bmspider.models import Quote


def get_hostname(url):
    return urlsplit(url).netloc


class BmServer:
    def __init__(self):
        template_path = os.path.join(os.path.dirname(__file__), "templates")
        self.jinja_env = Environment(loader=FileSystemLoader(template_path), autoescape=True)
        self.jinja_env.filters["hostname"] = get_hostname

        self.url_map = Map(
            [
                Rule("/", endpoint="home"),
            ]
        )

    def on_home(self, request):
        params_page = request.args.get("page", "1")
        page = int(params_page)
        next_page = page + 1
        previous_page = next_page - 1

        quotes_count = Quote.select().count()
        num_pages = math.ceil(float(quotes_count) / 10)
        range_pages = range(1, num_pages + 1)

        quotes = Quote.select().paginate(page, 10)

        context = dict(
            title="Home",
            quotes=quotes,
            next_page=next_page,
            previous_page=previous_page,
            range_pages=range_pages,
            page=page,
            num_pages=num_pages,
        )
        return self.render_template("home.html", **context)

    def error_404(self):
        response = self.render_template("404.html")
        response.status_code = 404
        return response

    def render_template(self, template_name, **context):
        t = self.jinja_env.get_template(template_name)
        return Response(t.render(context), mimetype="text/html")

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            return getattr(self, f"on_{endpoint}")(request, **values)
        except NotFound:
            return self.error_404()
        except HTTPException as e:
            return e

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)


def create_app(redis_host="localhost", redis_port=6379, with_static=True):
    app = BmServer()
    if with_static:
        app.wsgi_app = SharedDataMiddleware(
            app.wsgi_app, {"/static": os.path.join(os.path.dirname(__file__), "static")}
        )
    return app


if __name__ == "__main__":
    from werkzeug.serving import run_simple

    app = create_app()
    run_simple("0.0.0.0", 5000, app, use_debugger=True, use_reloader=True)
