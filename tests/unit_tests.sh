#!/bin/sh

set -e

pytest -n 6 --disable-pytest-warnings --cov-report term-missing --cov musicbot $@
coverage-badge -f -o doc/coverage.svg
# coverage report -m
