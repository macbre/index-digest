project_name = indexdigest
coverage_options = --include='$(project_name)/*' --omit='$(project_name)/test/*'

install:
	pip install -U -e .[dev]

test:
	pytest -x $(project_name)

coverage:
	rm -f .coverage*
	rm -rf htmlcov/*
	coverage run -p -m pytest -x $(project_name)
	coverage combine
	coverage html -d htmlcov $(coverage_options)
	coverage xml -i
	coverage report $(coverage_options)

lint:
	pylint $(project_name)/ --ignore=test

demo:
	docker run --network=host -t macbre/index-digest:latest mysql://index_digest:qwerty@127.0.0.1/index_digest --analyze-data --skip-checks=non_utf_columns --skip-tables=0028_no_time

sql-console:
	mysql --prompt='mysql@\h[\d]>' --protocol=tcp -uindex_digest -pqwerty index_digest

publish:
	# run git tag -a v0.0.0 before running make publish
	python setup.py sdist
	twine upload --skip-existing dist/*

# docker (tag with commit ID)
VERSION = "1.2.0-"$(shell git rev-parse --short HEAD)

build:
	@docker build -t macbre/index-digest:$(VERSION) . \
	&& docker tag macbre/index-digest:$(VERSION) macbre/index-digest:latest

push: build
	@docker push macbre/index-digest:$(VERSION) \
	&& docker push macbre/index-digest:latest

.PHONY: build
