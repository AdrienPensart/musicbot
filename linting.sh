#!/bin/sh

set -e

sh code-format.sh

echo "linting : ruff..."
uv run ruff check musicbot tests

echo "linting : pylint..."
uv run pylint musicbot tests

echo "linting : flake8..."
uv run flake8 musicbot tests

echo "static type checking : mypy..."
uv run mypy musicbot tests

# echo "static type checking : pyright..."
# uv run pyright

# echo "security checks : bandit..."
# uv run bandit -r musicbot

# echo "security checks : safety..."
# uv run safety check
