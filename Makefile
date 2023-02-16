format:
	autoflake -ir --remove-all-unused-imports .
	isort .
	black .

lint:
	flake8

mypy:
	mypy .

migrate:
	python manage.py makemigrations
	python manage.py migrate
	python manage.py loaddata data.json
	python manage.py tmd67_be/ac/data/ticket_product.json

run:
	sudo -E uwsgi --ini uwsgi.ini
