project_name = indexdigest
coverage_options = --include='$(project_name)/*' --omit='$(project_name)/test/*'

install:
	pip install -U -e .

test:
	py.test -x $(project_name)

coverage:
	rm -f .coverage*
	rm -rf htmlcov/*
	coverage run -p -m py.test -x $(project_name)
	coverage combine
	coverage html -d htmlcov $(coverage_options)
	coverage xml -i
	coverage report $(coverage_options)

lint:
	pylint $(project_name)/ --ignore=test

publish:
	python setup.py register -r pypi
	python setup.py sdist upload -r pypi

demo:
	index_digest mysql://index_digest:qwerty@localhost/index_digest

