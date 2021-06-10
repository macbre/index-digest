install:
	pip install -U -e .[dev]

test:
	pytest -vv -o log_cli=true -o log_cli_level=warning

coverage:
	pytest -vv --cov=indexdigest --cov-report=term --cov-report=xml --cov-report=html --cov-fail-under=93

lint:
	pylint indexdigest/ --ignore=test

demo:
	docker run --network=host -t macbre/index-digest:latest mysql://index_digest:qwerty@127.0.0.1/index_digest --analyze-data --skip-checks=non_utf_columns --skip-tables=0028_no_time

sql-console:
	mysql --prompt='mysql@\h[\d]>' --protocol=tcp -uindex_digest -pqwerty index_digest

publish:
	# run git tag -a v0.0.0 before running make publish
	python setup.py sdist
	twine upload --skip-existing dist/*

# docker (tag with commit ID)
VERSION = "1.2.1-"$(shell git rev-parse --short HEAD)

build:
	@docker build -t macbre/index-digest:$(VERSION) . \
	&& docker tag macbre/index-digest:$(VERSION) macbre/index-digest:latest

push: build
	@docker push macbre/index-digest:$(VERSION) \
	&& docker push macbre/index-digest:latest

.PHONY: build
