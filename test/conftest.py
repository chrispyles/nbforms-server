import datetime as dt
import pytest

from unittest import mock

from nbforms_server import create_app
from nbforms_server.models import (
  AttendanceSubmission,
  db,
  Notebook,
  Response,
  User,
)


@pytest.fixture
def app():
  """
  A fixture that provides a testing instance of the flask app.
  """
  # mock out os so that the instance path isn't actually created
  with mock.patch("nbforms_server.os"):
    app = create_app({
      "TESTING": True, 
      "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
  return app


@pytest.fixture(autouse=True)
def patch_cli_create_app(app):
  """
  A fixture that patches ``nbforms_server.__main__.create_app`` so that it returns the existing
  testing app instance.
  """
  with mock.patch("nbforms_server.__main__.create_app") as mocked_create_app:
    mocked_create_app.return_value = app
    yield


@pytest.fixture
def client(app):
  """
  A fixture that provides a flask testing client.
  """
  return app.test_client()


def make_timestamp(hour):
  return dt.datetime(2024, 2, 11, hour, 23, 57)


@pytest.fixture
def seed_data(app):
  """
  A fixture that seeds the database with users and notebooks.
  """
  users = [
    User.with_credentials("anakin", "skywalker"),
    User.with_credentials("obi-wan", "kenobi"),
    User.with_credentials("jarjar", "binks"),
    User.with_credentials("leia", "organa"),
    User(username="noauth_han", password_hash="", no_auth=True),
  ]

  notebooks = [
    Notebook(identifier="naboo"),
    Notebook(identifier="coruscant", attendance_open=True),
    Notebook(identifier="tatooine"),
  ]

  with app.app_context():
    for e in [*users, *notebooks]:
      db.session.add(e)
    db.session.commit()

  return users, notebooks


@pytest.fixture
def seed_responses(app, seed_data):
  """
  A fixture that seeds the database with users, notebooks, and responses.
  """
  users, notebooks = seed_data
  responses = [
    Response(user=users[0], notebook=notebooks[0], question_identifier="c3p0", response="anakin naboo c3p0", timestamp=make_timestamp(12)),
    Response(user=users[1], notebook=notebooks[0], question_identifier="c3p0", response="obi-wan naboo c3p0", timestamp=make_timestamp(13)),
    Response(user=users[2], notebook=notebooks[0], question_identifier="c3p0", response="jarjar naboo c3p0", timestamp=make_timestamp(14)),
    Response(user=users[3], notebook=notebooks[0], question_identifier="c3p0", response="leia naboo c3p0", timestamp=make_timestamp(15)),
    Response(user=users[0], notebook=notebooks[0], question_identifier="r2d2", response="anakin naboo r2d2", timestamp=make_timestamp(16)),
    Response(user=users[1], notebook=notebooks[0], question_identifier="r2d2", response="obi-wan naboo r2d2", timestamp=make_timestamp(17)),
    Response(user=users[0], notebook=notebooks[1], question_identifier="c3p0", response="anakin coruscant c3p0", timestamp=make_timestamp(18)),
    Response(user=users[1], notebook=notebooks[1], question_identifier="c3p0", response="obi-wan coruscant c3p0", timestamp=make_timestamp(19)),
    Response(user=users[2], notebook=notebooks[1], question_identifier="bb2", response="jarjar coruscant bb2", timestamp=make_timestamp(20)),
  ]

  with app.app_context():
    for e in responses:
      db.session.add(e)
    db.session.commit()


@pytest.fixture
def seed_attendance_submissions(app, seed_data):
  """
  A fixture that seeds the database with users, notebooks, and attendance submissions.
  """
  users, notebooks = seed_data
  submissions = [
    AttendanceSubmission(user=users[0], notebook=notebooks[0], was_open=False, timestamp=make_timestamp(12)),
    AttendanceSubmission(user=users[1], notebook=notebooks[0], was_open=True, timestamp=make_timestamp(13)),
    AttendanceSubmission(user=users[2], notebook=notebooks[0], was_open=True, timestamp=make_timestamp(13)),
    AttendanceSubmission(user=users[3], notebook=notebooks[0], was_open=False, timestamp=make_timestamp(14)),
  ]

  with app.app_context():
    for e in submissions:
      db.session.add(e)
    db.session.commit()


@pytest.fixture
def set_api_keys(app):
  """
  A fixture that provides a function to set the API keys for users. The function takes a single
  argument, a dictionary mapping usernames to API keys.
  """
  def do_set(usernames_to_keys):
    with app.app_context():
      for username, key in usernames_to_keys.items():
        u = db.session.query(User).filter_by(username=username).first()
        u.api_key = key
        db.session.add(u)
      db.session.commit()

  return do_set
