#!/bin/sh

export SETUPTOOLS_USE_DISTUTILS=stdlib

set -e

echo "security checks : bandit..."
poetry run bandit -r musicbot -s B608,B108

echo "security checks : safety..."
poetry run safety check

