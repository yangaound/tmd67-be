format:
	black .
	isort .

lint:
	flake8

mypy:
	mypy .
