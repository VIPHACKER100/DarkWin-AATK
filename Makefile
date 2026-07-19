.PHONY: install test clean

install:
	pip install -e .

test:
	pytest tests/ -v

clean:
	rm -rf logs/ reports/ __pycache__/
	find . -name "*.pyc" -delete
