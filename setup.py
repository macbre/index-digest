import re
from setuptools import setup, find_packages

# take the version
with open("indexdigest/__init__.py", "r") as fh:
    # e.g. VERSION = '1.5.0'
    last_line = fh.readlines()[-1]
    VERSION = re.search(r'[\d.]+', last_line).group(0)

# @see https://packaging.python.org/tutorials/packaging-projects/#creating-setup-py
with open("README.md", "r") as fh:
    long_description = fh.read()

# @see https://github.com/pypa/sampleproject/blob/master/setup.py
setup(
    name='indexdigest',
    version=VERSION,
    author='Maciej Brencz',
    author_email='maciej.brencz@gmail.com',
    license='MIT',
    description='Analyses your database queries and schema and suggests indices and schema improvements',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/macbre/index-digest',
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Database',

        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    packages=find_packages(),
    extras_require={
        'dev': [
            'coverage==6.4.4',
            'coveralls==3.3.1',
            'pylint==2.15.2',
            'pytest==7.1.3',
            'pytest-cov==3.0.0',
            'twine==4.0.1',
        ]
    },
    install_requires=[
        'docopt==0.6.2',
        'PyYAML==6.0',
        'mysqlclient==2.1.1',
        'sql_metadata==2.6.0',
        'termcolor==2.0.1',
        'yamlordereddictloader==0.4.0'
    ],
    entry_points={
        'console_scripts': [
            'add_linter=indexdigest.cli.add_linter:main',  # creates a new linter from a template
            'index_digest=indexdigest.cli.script:main',
        ],
    }
)
