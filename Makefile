format:
	autoflake -ir --remove-all-unused-imports .
	isort .
	black .

lint:
	flake8

mypy:
	mypy .

run:
	sudo uwsgi --ini uwsgi.ini
