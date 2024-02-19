"""A module for running nbforms-server as a WSGI application"""

from . import create_app


app = create_app()
