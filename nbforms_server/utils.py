"""Utilities for an nbforms server"""

import csv
import os

from io import StringIO
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
  from flask import Flask


DB_FILENAME = "nbforms_server.db"


def get_db_path(app: "Flask") -> str:
  """
  Get the server DB file path for the provided app instance.
  """
  return os.path.join(app.instance_path, DB_FILENAME)


def to_csv(l: List[List[str]]) -> str:
  """
  Convert a 2D list of strings into a CSV string.

  Args:
    l (``list[list[str]]``): the data

  Returns:
    ``str``: the CSV string
  """
  sio = StringIO()
  w = csv.writer(sio, dialect=csv.unix_dialect, quoting=csv.QUOTE_MINIMAL)
  w.writerows(l)
  return sio.getvalue()
