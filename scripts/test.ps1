pip install -qr requirements-dev.txt
pytest -v --cov=. --cov-report=term-missing
