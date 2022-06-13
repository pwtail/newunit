import json
import json
import os
import sys
from asyncio import iscoroutinefunction
from dataclasses import dataclass

import django
from django.urls import get_resolver
from django.urls.resolvers import RoutePattern, URLPattern, URLResolver


@dataclass
class UrlModule:
    path: str
    module: object

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
            if isinstance(url, URLResolver):
                new_path = ''.join((path, url.pattern._route))
                yield from cls._collect(new_path, url, result=result)

        if result and result[-1] is mod:
            del result[-1]

    @classmethod
    def collect(cls):
        return list(cls._collect())

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

        routes = []
        # named + plain

        for url in self.module.urlpatterns:
            route = ''.join((self.path, url.pattern._route))
            if self.is_async_endpoint(url):
                pattern = RoutePattern(route)
                uris.append(f"~{pattern.regex.pattern}$")
            elif isinstance(url, URLResolver):
                if not  isinstance(mod := url.urlconf_module, ModuleType):
                    # a hack
                    continue
                pattern = RoutePattern(route)
                if mod in modules:
                    name = mod.__name__
                    if name.endswith('.urls'):
                        name = name[:-5]
                    routes.append({
                        "match": {
                            "uri": f"~{pattern.regex.pattern}",
                        },
                        "action": {
                            "pass": f"routes/{name}",
                        },
                    })
        if uris:
            routes.append({
                "match": {
                    "uri": uris,
                },
                "action": {
                    "pass": "applications/asgi",
                }
            })
        routes.append({
            "action": {
                "pass": "applications/wsgi",
            }
        })
        name = self.module.__name__
        if name.endswith('.urls'):
            name = name[:-5]
        return {name: routes}


ModuleType = type(django)


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj.settings')
    django.setup()

    import proj.urls
    root = UrlModule(path='/', module=proj.urls)
    text = json.dumps(root.render_all())
    sys.stdout.write(text)

