"""Tests for ``nbforms_server.wsgi``"""

from flask import Flask

from nbforms_server.wsgi import app


def test_app():
  """
  Test that ``nbforms_server.wsgi`` provides an app instance.
  """
  assert isinstance(app, Flask)
