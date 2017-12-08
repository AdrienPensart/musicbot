# -*- coding: utf-8 -*-
from sanic import Sanic
from sanic.log import LOGGING_CONFIG_DEFAULTS

del LOGGING_CONFIG_DEFAULTS['loggers']['root']

app = Sanic(name='musicbot')
