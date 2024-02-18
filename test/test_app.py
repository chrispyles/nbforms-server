"""Tests for the nbforms server Flask app"""

import json
import pytest

from textwrap import dedent
from unittest import mock

from nbforms_server import create_app


@mock.patch("nbforms_server.os")
def test_create_app(mocked_os):
  """Test that ``create_app`` configures the app correctly."""
  app =  create_app()
  assert not app.testing
  assert mocked_os.makedirs.called_once_with(app.instance_path, exist_ok=True)

  assert create_app({'TESTING': True}).testing


@pytest.mark.parametrize(("username", "password", "want_code", "want_body"), (
  # existing user with correct password
  ("anakin", "skywalker", 200, "deadbeef"),
  # existing user with wrong password
  ("anakin", "vader", 400, "invalid login"),
  # new user
  ("jabba", "the hut", 200, "deadbeef"),
  # no username
  ("", "the hut", 400, "no username specified"),
  # no password
  ("jabba", "", 400, "no password specified"),
))
@mock.patch("nbforms_server.models.random")
def test_auth(mocked_random, client, seed_data, username, password, want_code, want_body):
  """Test the ``/auth`` route."""
  mocked_random.randbytes.return_value = b"\xde\xad\xbe\xef"

  res = client.post(
    "/auth",
    data = json.dumps({"username": username, "password": password}),
    content_type = "application/json",
  )

  assert res.status_code == want_code
  assert res.data.decode() == want_body


def test_submit():
  """Test the ``/submit`` route."""
  # TODO


def test_attendance():
  """Test the ``/attednance`` route."""
  # TODO


@pytest.mark.parametrize(("notebook", "questions", "user_hashes", "want_code", "want_body"), (
  # all questions
  ("naboo", None, None, 200, dedent("""\
    c3p0,r2d2
    anakin naboo c3p0,anakin naboo r2d2
    obi-wan naboo c3p0,obi-wan naboo r2d2
    jarjar naboo c3p0,
    leia naboo c3p0,
  """)),
  ("coruscant", None, None, 200, dedent("""\
    bb2,c3p0
    ,anakin coruscant c3p0
    ,obi-wan coruscant c3p0
    jarjar coruscant bb2,
  """)),
  # notebook exists but has no responses
  ("tatooine", None, None, 400, "no responses found"),
  # test that falsey versions of questions and user_hashes behave the same as unspecified
  ("naboo", [], False, 200, dedent("""\
    c3p0,r2d2
    anakin naboo c3p0,anakin naboo r2d2
    obi-wan naboo c3p0,obi-wan naboo r2d2
    jarjar naboo c3p0,
    leia naboo c3p0,
  """)),
  # nonexistant notebook
  ("mustafar", None, None, 400, "no responses found"),
  # limit questions
  ("naboo", ["r2d2"], None, 200, dedent("""\
    r2d2
    anakin naboo r2d2
    obi-wan naboo r2d2
  """)),
  # include user hashes
  ("naboo", None, True, 200, dedent("""\
    user,c3p0,r2d2
    370b126df07859afa569,anakin naboo c3p0,anakin naboo r2d2
    b642fa7c51f517fa4092,obi-wan naboo c3p0,obi-wan naboo r2d2
    b5d7f583fe24ed18083a,jarjar naboo c3p0,
    b0dea5555379c9e3384d,leia naboo c3p0,
  """)),
  # no notebook
  ("", None, None, 400, "no notebook specified")
))
def test_data(client, seed_data, notebook, questions, user_hashes, want_code, want_body):
  """Test the ``/data`` route."""
  body = {"notebook": notebook}
  if questions is not None:
    body["questions"] = questions
  if user_hashes is not None:
    body["user_hashes"] = user_hashes

  res = client.get(
    "/data",
    data = json.dumps(body),
    content_type = "application/json",
  )

  assert res.status_code == want_code
  assert res.data.decode() == want_body
