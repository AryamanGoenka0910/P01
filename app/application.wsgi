#! /usr/bin/python3.8
activate_this = '/home/haotian/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))
import logging
import sys
logging.basicConfig(stream=sys.stderr)
from app import app as application