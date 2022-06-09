import inspect
import json
import os
import sys
from asyncio import iscoroutinefunction
from dataclasses import dataclass

import django
from django.core.handlers.asgi import ASGIRequest
from django.urls import get_resolver
from django.urls.resolvers import RoutePattern, URLPattern, URLResolver
from django.utils.module_loading import import_string




def wrap(fn):
    assert not getattr(fn, 'wrapped', None)
    if not inspect.isfunction(fn):
        return fn

    def wrapper(request):
        assert isinstance(request, ASGIRequest) == iscoroutinefunction(fn)
        return fn(request)

    return wrapper


def wrap_all():
    for fn, tup in get_resolver().reverse_dict.items():
        new_fn = wrap(fn)
        try:
            mod = import_string(fn.__module__)
        except Exception as ex:
            if fn == 'redoc':
                1
        if getattr(mod, fn.__name__, None) is fn:
            setattr(mod, fn.__name__, new_fn)


"""
nymph.urls
get_path()  .urls

"""


# асинх. урлы только в модулях

def render_urls(path, urlconf_module, result=None):
    if result is None:
        result = {}
    name = urlconf_module.__name__
    uris = []
    for url in urlconf_module.urlpatterns:
        if not url.callback or not iscoroutinefunction(url.callback):
            continue
        route = ''.join(path, url.pattern._route)
        pattern = RoutePattern(route, is_endpoint=True)
        uris.append(f"~{pattern.regex}")

    return {
        name: [
            {
                "match": {
                    "uri": uris,
                },
                "action": {
                    "pass": "applications/hesperides",
                }
            }
        ]
    }


@dataclass
class UrlModule:
    path: str
    module: object

    # @classmethod
    # def _collect(cls, path='', resolver=None, result=None):
    #     if resolver is None:
    #         resolver = get_resolver()
    #     if result is None:
    #         result = {}
    #     if isinstance(resolver.urlconf_module, ModuleType):
    #         yield UrlModule(path, resolver.urlconf_module)
    #     for url in resolver.url_patterns:
    #         if isinstance(url, URLPattern):
    #             continue
    #         new_path = ''.join((path, url.pattern._route))
    #         yield from cls._collect(new_path, url)

    @classmethod
    def _collect(cls, path='/', resolver=None, result=None):
        if resolver is None:
            resolver = get_resolver()
        if result is None:
            result = []
        if isinstance(mod := resolver.urlconf_module, ModuleType):
            mod = cls(path, mod)
            result.append(mod)
        if any(cls.is_async_endpoint(url) for url in resolver.url_patterns):
            yield from result
            del result[:]
        for url in resolver.url_patterns:
            if not isinstance(url, URLPattern) and isinstance(url, URLResolver):
                new_path = ''.join((path, url.pattern._route))
                yield from cls._collect(new_path, url, result=result)

        if result and result[-1] is mod:
            del result[-1]

    @classmethod
    def collect(cls):
        return list(cls._collect())

    # TODO routes/

    @staticmethod
    def is_async_endpoint(url):
        return isinstance(url, URLPattern) and iscoroutinefunction(url.callback)

    @classmethod
    def render_all(cls):
        collected = cls.collect()
        modules = set(m.module for m in collected)
        result = {}
        for m in collected:
            if routes := m.render(modules):
                result.update(routes)
        return {'routes': result}

    def render(self, modules):
        uris = []
        items = {}
        for url in self.module.urlpatterns:
            route = ''.join((self.path, url.pattern._route))
            if self.is_async_endpoint(url):
                pattern = RoutePattern(route)
                uris.append(f"~{pattern.regex.pattern}$")
            elif isinstance(url, URLResolver) and isinstance(mod := url.urlconf_module, ModuleType):
                pattern = RoutePattern(route)
                if mod in modules:
                    items.update({
                        self.module.__name__: [{
                            "match": {
                                "uri": f"~{pattern.regex.pattern}",
                            },
                            "action": {
                                "pass": f"routes/{mod.__name__}",
                            }
                        }, {
                            "action": {
                                "pass": "applications/nereids",
                            }
                        }]})
        if uris:
            name = self.module.__name__
            items.update({
                name: [
                    {
                        "match": {
                            "uri": uris,
                        },
                        "action": {
                            "pass": "applications/hesperides",
                        }
                    },
                    {
                        "action": {
                            "pass": "applications/nereids",
                        }
                    }
                ]
            })
        return items


ModuleType = type(django)

1

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj.settings')
    django.setup()

    import proj.urls
    root = UrlModule(path='/', module=proj.urls)
    text = json.dumps(root.render_all())
    sys.stdout.write(text)

