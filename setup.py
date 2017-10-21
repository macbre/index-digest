from setuptools import setup, find_packages

# @see https://github.com/pypa/sampleproject/blob/master/setup.py
setup(
    name='indexdigest',
    version='0.1.0',
    author='Maciej Brencz',
    author_email='maciej.brencz@gmail.com',
    description='Analyses your database queries and schema and suggests indices improvements',
    url='https://github.com/macbre/index-digest',
    packages=find_packages(),
    install_requires=[
        'docopt==0.6.2',
        'coverage==4.4.1',
        'pylint==1.7.4',
        'pytest==3.2.3',
        'mysqlclient==1.3.12',
    ],
    entry_points={
        'console_scripts': [
            'index_digest=indexdigest.cli:main',
        ],
    }
)
