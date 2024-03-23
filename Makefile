install:
	pip install -r requirements.txt

test:
	python -m unittest tests/test_monarchmoney.py

lint:
	black monarchmoney/ tests/

typecheck:
	pyre check

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
