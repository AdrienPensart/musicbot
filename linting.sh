#!/bin/bash

set -e

echo "linting : pylint..."
poetry run pylint musicbot tests

echo "linting : flake8..."
poetry run flake8 musicbot tests

echo "static type checking : mypy..."
poetry run mypy musicbot tests
