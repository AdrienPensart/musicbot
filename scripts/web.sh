#!/bin/bash

gunicorn lib.server:app --pythonpath=$(pwd) --bind 127.0.0.1:1337 --worker-class sanic.worker.GunicornWorker
