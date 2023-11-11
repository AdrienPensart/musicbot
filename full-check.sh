#!/bin/sh

export SETUPTOOLS_USE_DISTUTILS=stdlib

set -e
trap '[ $? -eq 0 ] && exit 0 || echo "$0 FAILED"' EXIT

# poetry run edgedb-py --dsn edgedb://musicbot:musicbot@127.0.0.1:5656 --tls-security insecure --dir musicbot --file musicbot/queries.py

sh linting.sh
sh gen-doc.sh
sh tests-check.sh

echo "Running unit tests"
poetry run pytest
poetry run coverage-badge -f -o doc/coverage.svg
git add doc/coverage.svg

exit 0
