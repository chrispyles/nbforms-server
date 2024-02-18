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
  # mock out os so that the instance path isn't actually created
  with mock.patch("nbforms_server.os"):
    app = create_app({
      "TESTING": True, 
      "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
  return app


@pytest.fixture
def client(app):
  return app.test_client()


@pytest.fixture
def runner(app):
  return app.test_cli_runner()


def make_timestamp(hour):
  return dt.datetime(2024, 2, 11, hour, 23, 57)


@pytest.fixture
def seed_data(app):
  users = [
    User.with_credentials("anakin", "skywalker"),
    User.with_credentials("obi-wan", "kenobi"),
    User.with_credentials("jarjar", "binks"),
    User.with_credentials("leia", "organa"),
  ]
  notebooks = [
    Notebook(identifier="naboo"),
    Notebook(identifier="coruscant"),
    Notebook(identifier="tatooine"),
  ]
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
    # TODO: duplicate responses aren't handled yet but once they are this should be uncommented
    # Response(user=users[2], notebook=notebooks[1], question_identifier="bb2", response="jarjar coruscant bb2 2", timestamp=make_timestamp(21)),
  ]
  submissions = [
    AttendanceSubmission(user=users[0], notebook=notebooks[0], was_open=False, timestamp=make_timestamp(12)),
    AttendanceSubmission(user=users[1], notebook=notebooks[0], was_open=True, timestamp=make_timestamp(13)),
    AttendanceSubmission(user=users[2], notebook=notebooks[0], was_open=True, timestamp=make_timestamp(13)),
    AttendanceSubmission(user=users[3], notebook=notebooks[0], was_open=False, timestamp=make_timestamp(14)),
  ]
  with app.app_context():
    for e in [*users, *notebooks, *responses, *submissions]:
      db.session.add(e)
    db.session.commit()
