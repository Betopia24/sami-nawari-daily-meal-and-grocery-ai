#!/usr/bin/env sh
set -eu
pytest -q -m "not integration" --cov=app --cov-report=term-missing
