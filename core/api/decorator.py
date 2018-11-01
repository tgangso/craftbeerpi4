from aiohttp_auth import auth

def composed(*decs):
    def deco(f):
        for dec in reversed(decs):
            f = dec(f)
        return f
    return deco

def request_mapping(path, name=None, method="GET", auth_required=True):

    def on_http_request(path, name=None):
        def real_decorator(func):
            func.route = True
            func.path = path
            func.name = name
            func.method = method
            return func

        return real_decorator

    if auth_required is True:
        return composed(
            on_http_request(path,  name),
            auth.auth_required
        )
    else:
        return composed(
            on_http_request(path, name)
        )

def on_websocket_message(path, name=None):
    def real_decorator(func):
        func.ws = True
        func.key = path
        func.name = name
        return func

    return real_decorator

def on_event(topic):
    def real_decorator(func):
        func.eventbus = True
        func.topic = topic
        return func

    return real_decorator

def action(key, parameters):
    def real_decorator(func):
        func.action = True
        func.key = key
        func.parameters = parameters
        return func

    return real_decorator

def on_mqtt_message(topic):
    def real_decorator(func):
        func.mqtt = True
        func.topic = topic
        return func

    return real_decorator


def background_task(name, interval):
    def real_decorator(func):
        func.background_task = True
        func.name = name
        func.interval = interval
        return func

    return real_decorator


def entry_exit(f):
    def new_f():
        print("Entering", f.__name__)
        f()
        print("Exited", f.__name__)
    return new_f