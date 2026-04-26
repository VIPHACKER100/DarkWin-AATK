.PHONY: install test clean

install:
	pip install -r requirements.txt
	pip install -e .

test:
	pytest tests/ -v

clean:
	rm -rf logs/*.log
	rm -rf reports/*
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete
