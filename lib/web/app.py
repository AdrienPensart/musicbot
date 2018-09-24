from sanic import Sanic
from sanic.log import LOGGING_CONFIG_DEFAULTS
from ..collection import Collection

del LOGGING_CONFIG_DEFAULTS['loggers']['root']

app = Sanic(name='musicbot', strict_slashes=True)
