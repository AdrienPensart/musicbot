#!/bin/bash

set -e

echo "updating poetry deps..."
poetry update

echo "generating setup.py"
poetry run poetry2setup > setup.py

echo "generating requirements.txt"
poetry export -f requirements.txt --without-hashes -o requirements.txt

echo "generating requirements-dev.txt"
poetry export -f requirements.txt --dev --without-hashes -o requirements-dev.txt
