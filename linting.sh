#!/bin/sh

export SETUPTOOLS_USE_DISTUTILS=stdlib

set -e

sh code-format.sh

echo "linting : ruff..."
poetry run ruff check musicbot tests

echo "linting : pylint..."
poetry run pylint musicbot tests

echo "linting : flake8..."
poetry run flake8 musicbot tests

echo "static type checking : mypy..."
poetry run mypy musicbot tests

# echo "static type checking : pyright..."
# poetry run pyright

# echo "security checks : bandit..."
# poetry run bandit -r musicbot

# echo "security checks : safety..."
# poetry run safety check
