# -*- coding: utf-8 -*-
from sanic_limiter import Limiter, get_remote_address
from .app import app

limiter = Limiter(app, global_limits=['1 per hour', '10 per day'], key_func=get_remote_address)
