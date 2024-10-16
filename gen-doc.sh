#!/bin/sh

export SETUPTOOLS_USE_DISTUTILS=stdlib

set -e

echo "rst-linting pass 1..."
uv run rst-lint doc/help.rst

echo "doc generation..."
uv run musicbot readme --output rst > README.rst

echo "rst-linting pass 2..."
uv run rst-lint README.rst
