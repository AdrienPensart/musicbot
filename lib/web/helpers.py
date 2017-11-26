# -*- coding: utf-8 -*-
import os
from sanic.response import json, html
from jinja2 import Environment, FileSystemLoader
from functools import wraps
THIS_DIR = os.path.dirname(os.path.abspath(__file__))

env = Environment(loader=FileSystemLoader(os.path.join(THIS_DIR, 'templates')), enable_async=True)


async def template(tpl, headers=None, **kwargs):
    template = env.get_template(tpl)
    rendered_template = await template.render_async(**kwargs)
    return html(rendered_template, headers=headers)


def basicauth():
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            # run some method that checks the request
            # for the client's authorization status
            # is_authorized = check_request_for_authorization_status(request)
            is_authorized = None

            if is_authorized:
                # the user is authorized.
                # run the handler method and return the response
                response = await f(request, *args, **kwargs)
                return response
            else:
                # the user is not authorized.
                return json({'status': 'not_authorized'}, 403)
        return decorated_function
    return decorator
