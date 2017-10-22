"""
A module containing command-line tool
"""
import logging

from os import getenv

if getenv('DEBUG') == '1':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(name)-35s %(levelname)-8s %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S"
    )
