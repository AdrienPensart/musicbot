#!/bin/sh

set -e

uv run isort musicbot tests
uv run black musicbot tests

