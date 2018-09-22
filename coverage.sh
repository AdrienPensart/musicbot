#!/bin/sh

set -e

export MB_DB=musicbot_test
export MB_DB_PASSWORD=musicbot
coverage run --source lib -m test.test
coverage-badge -f -o doc/coverage.svg
coverage report -m
