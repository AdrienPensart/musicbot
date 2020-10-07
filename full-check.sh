#!/bin/sh

set -e
trap '[ $? -eq 0 ] && exit 0 || echo "$0 FAILED"' EXIT

echo "updating poetry deps..."
poetry update

echo "generating setup.py"
poetry run dephell deps convert

echo "generating requirements.txt"
poetry run dephell deps convert --from-format=poetry --from-path=pyproject.toml --to-format=pip --to-path=requirements.txt --envs main

echo "generating requirements-dev.txt"
poetry run dephell deps convert --from-format=poetry --from-path=pyproject.toml --to-format=pip --to-path=requirements-dev.txt --envs main dev

echo "linting : pylint..."
poetry run pylint musicbot tests doc

echo "linting : flake8..."
poetry run flake8 musicbot tests doc

echo "static type checking : mypy..."
poetry run mypy musicbot tests doc

echo "static type checking : checking..."
poetry run pytype musicbot tests doc -j auto -k

kernel=`uname -r`
case "$kernel" in
*microsoft*) echo "No unit testing because docker not available" ;;
*       )
    echo "Running unit tests"
    poetry run pytest
    poetry run coverage-badge -f -o doc/coverage.svg
    git add doc/coverage.svg
    ;;
esac

echo "rst-linting pass 1..."
poetry run rst-lint doc/help.rst
echo "doc generation..."
poetry run doc/gen.py > README.rst
echo "rst-linting pass 2..."
poetry run rst-lint README.rst

exit 0
