import json
import logging
from collections import defaultdict
from fnmatch import fnmatch
from functools import partial

from eventlet.event import Event
from nameko.exceptions import serialize
from nameko.web.server import WebServer
from werkzeug.exceptions import BadRequest, HTTPException
from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Request, Response


from nameko_stripe.handlers.webhook import WebhookHandler


logger = logging.getLogger(__name__)


class Router:
    def __init__(self, container, handlers=None):
        self.container = container
        self.handlers = handlers or set()

    def __call__(self, request):
        return self.handle(request)

    def handle(self, request):
        events = set()
        event_name = self.parse_event_name(request)
        for handler in self.handlers:
            if fnmatch(event_name, handler.event_name):
                event = Event()
                events.add(event)
                handler.handle_request(request, event)
        [event.wait() for event in events]

    def parse_event_name(self, request):
        data = request.data.decode("utf8")
        try:
            return json.loads(data)["type"]
        except Exception:
            logger.warning("Cannot parse Stripe webhook", exc_info=True)
            raise BadRequest("Cannot parse Stripe webhook")


class EventServer(WebServer):
    def make_url_map(self):

        routes = defaultdict(list)

        for provider in self._providers:
            routes[(provider.url, provider.method)].append(provider)

        url_map = Map()

        for route, providers in routes.items():
            url, method = route
            rule = Rule(url, methods=method.split(","))
            rule.endpoint = Router(self.container, providers)
            url_map.add(rule)

        return url_map

    def get_wsgi_app(self):
        return WsgiApp(self)


class WsgiApp(object):
    def __init__(self, server):
        self.url_map = server.make_url_map()

    def __call__(self, environ, start_response):
        request = Request(environ)
        adapter = self.url_map.bind_to_environ(environ)
        try:
            handle, values = adapter.match()
            request.path_values = values
            handle(request)
        except HTTPException as exc:
            rv = exc
        except Exception as exc:
            error_dict = serialize(exc)
            payload = u"Error: {exc_type}: {value}\n".format(**error_dict)
            rv = Response(payload, status=500)
        else:
            rv = Response("OK", status=200)
        return rv(environ, start_response)


class EventHandler(WebhookHandler):

    server = EventServer()

    def __init__(
        self, event_name, path=None, api_key=None, endpoint_secret=None, **kwargs
    ):
        self.event_name = event_name
        super(EventHandler, self).__init__(
            path=path, api_key=api_key, endpoint_secret=endpoint_secret, **kwargs
        )

    def get_entrypoint_parameters(self, request):

        event = self.parse_event(request)

        args = (event["type"], event)
        kwargs = request.path_values

        return args, kwargs

    def handle_request(self, request, event):
        context_data = self.server.context_data_from_headers(request)
        args, kwargs = self.get_entrypoint_parameters(request)

        self.check_signature(args, kwargs)
        self.container.spawn_worker(
            self,
            args,
            kwargs,
            context_data=context_data,
            handle_result=partial(self.handle_result, event),
        )

    def handle_result(self, event, worker_ctx, result, exc_info):
        event.send(result, exc_info)
        return result, exc_info


event_handler = EventHandler.decorator
