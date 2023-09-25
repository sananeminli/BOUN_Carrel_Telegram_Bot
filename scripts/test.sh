#!/usr/bin/env bash

set -euxo pipefail

pip install -qr requirements-dev.txt
pytest -v --cov=. --cov-report=term-missing
