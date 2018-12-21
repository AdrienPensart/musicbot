#!/bin/sh

set -e

pytest -n 4 --cov-report term-missing --cov musicbot $@
coverage-badge -f -o doc/coverage.svg
coverage report -m
