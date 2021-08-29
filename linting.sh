#!/bin/bash

set -e

echo "sql linting..."
for sql in $(find musicbot/schema -type f); do
    squawk --verbose --exclude=prefer-robust-stmts --exclude=require-concurrent-index-creation $sql
done

echo "linting : pylint..."
poetry run pylint musicbot tests

echo "linting : flake8..."
poetry run flake8 musicbot tests

echo "static type checking : mypy..."
poetry run mypy musicbot tests
