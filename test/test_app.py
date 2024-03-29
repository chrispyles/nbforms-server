"""Tests for the nbforms server Flask app"""

import datetime as dt
import json
import os
import pytest

from textwrap import dedent
from unittest import mock

from nbforms_server import create_app
from nbforms_server.models import AttendanceSubmission, db, Notebook, Response, User


count = 0
def make_dt(force_count=None):
  """Create a ``dt.datetime`` object. Used for stubbing out ``dt.datetime.now``."""
  global count
  if force_count is None:
    count += 1
  return dt.datetime(2024, 2, 20, count if force_count is None else force_count, 13, 14)


@pytest.fixture(autouse=True)
def reset_count():
  """Reset the ``count`` global before each test case."""
  global count
  count = 0


@mock.patch("nbforms_server.os")
def test_create_app(mocked_os):
  """Test that ``create_app`` configures the app correctly."""
  app =  create_app()
  assert not app.testing
  assert mocked_os.makedirs.called_once_with(app.instance_path, exist_ok=True)

  assert create_app({'TESTING': True}).testing


@mock.patch("nbforms_server.render_template")
def test_index(mocked_render_template, client):
  """Test the ``/`` route."""
  res = client.get("/")

  assert res.status_code == 200
  mocked_render_template.assert_called_once_with("index.html")


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
  ("anakin", "", 400, "no password specified"),
  # new user no password
  ("jabba", "", 400, "no password specified"),
  # no auth user
  ("noauth_han", "solo", 400, "invalid login"),
))
@mock.patch("nbforms_server.models.random")
def test_auth(mocked_random, app, client, seed_data, username, password, want_code, want_body):
  """Test the ``/auth`` route."""
  mocked_random.randbytes.return_value = b"\xde\xad\xbe\xef"

  res = client.post(
    "/auth",
    data = json.dumps({"username": username, "password": password}),
    content_type = "application/json",
  )

  assert res.status_code == want_code
  assert res.data.decode() == want_body

  with app.app_context():
    seed_usernames = [db.session.merge(u).username for u in seed_data[0]]

  with app.app_context():
    u = db.session.query(User).filter_by(username=username).first()

  # check that the API key in the DB is correct
  if not username or (username not in seed_usernames and not password):
    # in this case, the user does not exist but did not provide a password, so no user row was
    # created
    assert u is None
  else:
    assert u.api_key == ("deadbeef" if want_code == 200 else None)


@mock.patch("nbforms_server.models.random")
@mock.patch("nbforms_server.models.ph")
def test_auth_password_rehash(mocked_ph, mocked_random, app, client, seed_data):
  """Test the ``/auth`` route when a password rehash is required."""
  mocked_random.randbytes.return_value = b"\xde\xad\xbe\xef"
  mocked_ph.check_needs_rehash.return_value = True
  mocked_ph.hash.return_value = "skywalker (but hashed)"

  res = client.post(
    "/auth",
    data = json.dumps({"username": "anakin", "password": "skywalker"}),
    content_type = "application/json",
  )

  assert res.status_code == 200
  assert res.data.decode() == "deadbeef"
  mocked_ph.hash.assert_called_with("skywalker")

  # check that the API key in the DB is correct
  with app.app_context():
    u = db.session.query(User).filter_by(username="anakin").first()
    assert u.password_hash == "skywalker (but hashed)"


@mock.patch.dict(os.environ, {"NBFORMS_SERVER_NO_AUTH_REQUIRED": "true"})
@mock.patch("nbforms_server.models.random")
def test_no_auth_required(mocked_random, app, client):
  """Test the ``/auth`` route when ``NBFORMS_SERVER_NO_AUTH_REQUIRED`` is true."""
  mocked_random.randbytes.return_value = b"\xde\xad\xbe\xef"

  res = client.post("/auth")

  assert res.status_code == 200
  assert res.data.decode() == "deadbeef"

  with app.app_context():
    users = db.session.query(User).all()

  assert len(users) == 1
  assert users[0].username == "noauth_deadbeef"
  assert users[0].password_hash == ""
  assert users[0].api_key == "deadbeef"


@pytest.mark.parametrize(("body", "want_code", "want_body", "want_responses"), (
  # create new response
  (
    {
      "api_key": "deadbeef",
      "notebook": "tatooine",
      "responses": [
        {
          "identifier": "c3p0",
          "response": "obi-wan tatooine c3p0",
        },
      ],
    },
    200,
    "ok",
    [
      {
        "user_id": 2,
        "notebook_id": 3,
        "question_identifier": "c3p0",
        "response": "obi-wan tatooine c3p0",
        "timestamp": make_dt(1),
      },
    ],
  ),
  # nonexistent notebook
  (
    {
      "api_key": "deadbeef",
      "notebook": "mustafar",
      "responses": [
        {
          "identifier": "c3p0",
          "response": "obi-wan mustafar c3p0",
        },
        {
          "identifier": "r2d2",
          "response": "obi-wan mustafar r2d2",
        },
      ],
    },
    200,
    "ok",
    [
      {
        "user_id": 2,
        "notebook_id": 4,
        "question_identifier": "c3p0",
        "response": "obi-wan mustafar c3p0",
        "timestamp": make_dt(1),
      },
      {
        "user_id": 2,
        "notebook_id": 4,
        "question_identifier": "r2d2",
        "response": "obi-wan mustafar r2d2",
        "timestamp": make_dt(2),
      },
    ],
  ),
  # nonexistent API key
  (
    {
      "api_key": "notdeadbeef",
      "notebook": "tatooine",
      "responses": [
        {
          "identifier": "c3p0",
          "response": "obi-wan tatooine c3p0",
        },
      ],
    },
    400,
    "no such user",
    [],
  ),
  # no API key
  (
    {
      "notebook": "tatooine",
      "responses": [
        {
          "identifier": "c3p0",
          "response": "obi-wan tatooine c3p0",
        },
      ],
    },
    400,
    "no api_key specified",
    [],
  ),
  # no notebook
  (
    {
      "api_key": "deadbeef",
      "responses": [
        {
          "identifier": "c3p0",
          "response": "obi-wan tatooine c3p0",
        },
      ],
    },
    400,
    "no notebook specified",
    [],
  ),
  # no responses
  (
    {
      "api_key": "deadbeef",
      "notebook": "tatooine",
    },
    400,
    "no responses specified",
    [],
  ),
  # response has no identifier
  (
    {
      "api_key": "deadbeef",
      "notebook": "tatooine",
      "responses": [
        {
          "response": "obi-wan tatooine c3p0",
        },
      ],
    },
    400,
    "invalid response: {'response': 'obi-wan tatooine c3p0'}",
    [],
  ),
  # response has no response
  (
    {
      "api_key": "deadbeef",
      "notebook": "tatooine",
      "responses": [
        {
          "identifier": "c3p0",
        },
      ],
    },
    200,
    "ok",
    [
      {
        "user_id": 2,
        "notebook_id": 3,
        "question_identifier": "c3p0",
        "response": "",
        "timestamp": make_dt(1),
      },
    ],
  ),
))
@mock.patch("nbforms_server.dt")
def test_submit(
  mocked_dt,
  app,
  client,
  seed_data,
  set_api_keys,
  body,
  want_code,
  want_body,
  want_responses,
):
  """Test the ``/submit`` route."""
  set_api_keys({"obi-wan": "deadbeef"})
  mocked_dt.datetime.now.side_effect = make_dt

  res = client.post("/submit", data=json.dumps(body), content_type="application/json")

  assert res.status_code == want_code, res.data.decode()
  assert res.data.decode() == want_body

  with app.app_context():
    responses = db.session.query(Response).order_by(Response.timestamp).all()

  assert len(responses) == len(want_responses)
  for i, (r, wr) in enumerate(zip(responses, want_responses)):
    for k, v in wr.items():
      assert getattr(r, k) == v, f"wrong value for attribute '{k}' in response {i}"


@mock.patch("nbforms_server.dt")
def test_submit_update_old_responses(mocked_dt, app, client, seed_responses, set_api_keys):
  """Test the ``/submit`` route handling for updating existing responses."""
  set_api_keys({"obi-wan": "deadbeef"})
  mocked_dt.datetime.now.side_effect = make_dt

  res = client.post(
    "/submit",
    data = json.dumps({
      "api_key": "deadbeef",
      "notebook": "naboo",
      "responses": [
        {
          "identifier": "c3p0",
          "response": "obi-wan naboo c3p0 2",
        },
        {
          "identifier": "r2d2",
          "response": "obi-wan naboo r2d2 2",
        },
      ],
    }),
    content_type = "application/json",
  )

  assert res.status_code == 200, res.data.decode()
  assert res.data.decode() == "ok"

  with app.app_context():
    responses = (
      db.session
        .query(Response)
        .filter_by(user_id=2, notebook_id=1)
        .order_by(Response.timestamp)
        .all()
    )

  want_responses = [
    {
      "user_id": 2,
      "notebook_id": 1,
      "question_identifier": "c3p0",
      "response": "obi-wan naboo c3p0 2",
      "timestamp": make_dt(1),
    },
    {
      "user_id": 2,
      "notebook_id": 1,
      "question_identifier": "r2d2",
      "response": "obi-wan naboo r2d2 2",
      "timestamp": make_dt(2),
    },
  ]

  assert len(responses) == len(want_responses)
  for i, (r, wr) in enumerate(zip(responses, want_responses)):
    for k, v in wr.items():
      assert getattr(r, k) == v, f"wrong value for attribute '{k}' in response {i}"


@pytest.mark.parametrize(("body", "want_code", "want_body", "want_submissions"), (
  # open
  (
    {
      "api_key": "deadbeef",
      "notebook": "tatooine",
    },
    200,
    "ok",
    [
      {
        "user_id": 2,
        "notebook_id": 3,
        "timestamp": make_dt(1),
        "was_open": True,
      },
    ],
  ),
  # closed
  (
    {
      "api_key": "deadbeef",
      "notebook": "naboo",
    },
    200,
    "ok",
    [
      {
        "user_id": 2,
        "notebook_id": 1,
        "timestamp": make_dt(1),
        "was_open": False,
      },
    ],
  ),
  # nonexistent notebook
  (
    {
      "api_key": "deadbeef",
      "notebook": "mustafar",
    },
    200,
    "ok",
    [
      {
        "user_id": 2,
        "notebook_id": 4,
        "timestamp": make_dt(1),
        "was_open": False,
      },
    ],
  ),
  # nonexistent API key
  (
    {
      "api_key": "notdeadbeef",
      "notebook": "tatooine",
    },
    400,
    "no such user",
    [],
  ),
  # no API key
  (
    {
      "notebook": "tatooine",
    },
    400,
    "no api_key specified",
    [],
  ),
  # no notebook
  (
    {
      "api_key": "deadbeef",
    },
    400,
    "no notebook specified",
    [],
  ),
))
@mock.patch("nbforms_server.dt")
def test_attendance(
  mocked_dt,
  app,
  client,
  seed_data,
  set_api_keys,
  body,
  want_code,
  want_body,
  want_submissions,
):
  """Test the ``/attendance`` route."""
  set_api_keys({"obi-wan": "deadbeef"})
  mocked_dt.datetime.now.side_effect = make_dt
  
  # open attendance for tatooine
  with app.app_context():
    n = db.session.query(Notebook).filter_by(identifier="tatooine").first()
    n.attendance_open = True
    db.session.add(n)
    db.session.commit()

  res = client.post("/attendance", data=json.dumps(body), content_type="application/json")

  assert res.status_code == want_code, res.data.decode()
  assert res.data.decode() == want_body

  with app.app_context():
    submissions = db.session.query(AttendanceSubmission).order_by(AttendanceSubmission.timestamp).all()

  assert len(submissions) == len(want_submissions)
  for i, (r, wr) in enumerate(zip(submissions, want_submissions)):
    for k, v in wr.items():
      assert getattr(r, k) == v, f"wrong value for attribute '{k}' in submission {i}"


@mock.patch("nbforms_server.dt")
def test_attendance_multiple_submissions(mocked_dt, app, client, seed_attendance_submissions, set_api_keys):
  """Test the ``/attendance`` route handling for multiple attendance submissions."""
  set_api_keys({"obi-wan": "deadbeef"})
  mocked_dt.datetime.now.side_effect = make_dt

  res = client.post(
    "/attendance",
    data = json.dumps({
      "api_key": "deadbeef",
      "notebook": "naboo",
    }),
    content_type = "application/json",
  )

  assert res.status_code == 200, res.data.decode()
  assert res.data.decode() == "ok"

  with app.app_context():
    submissions = (
      db.session
        .query(AttendanceSubmission)
        .filter_by(user_id=2, notebook_id=1)
        .order_by(AttendanceSubmission.timestamp)
        .all()
    )

  want_submissions = [
    {
      "user_id": 2,
      "notebook_id": 1,
      "was_open": True,
      "timestamp": dt.datetime(2024, 2, 11, 13, 23, 57),
    },
    {
      "user_id": 2,
      "notebook_id": 1,
      "was_open": False,
      "timestamp": make_dt(1),
    },
  ]

  assert len(submissions) == len(want_submissions)
  for i, (r, wr) in enumerate(zip(submissions, want_submissions)):
    for k, v in wr.items():
      assert getattr(r, k) == v, f"wrong value for attribute '{k}' in submission {i}"


@pytest.mark.parametrize(("notebook", "questions", "user_hashes", "want_code", "want_body"), (
  # all questions
  ("naboo", None, None, 200, dedent("""\
    c3p0,r2d2
    anakin naboo c3p0,anakin naboo r2d2
    jarjar naboo c3p0,
    leia naboo c3p0,
    obi-wan naboo c3p0,obi-wan naboo r2d2
  """)),
  ("coruscant", None, None, 200, dedent("""\
    bb2,c3p0
    ,anakin coruscant c3p0
    jarjar coruscant bb2,
    ,obi-wan coruscant c3p0
  """)),
  # notebook exists but has no responses
  ("tatooine", None, None, 400, "no responses found"),
  # test that falsey versions of questions and user_hashes behave the same as unspecified
  ("naboo", [], False, 200, dedent("""\
    c3p0,r2d2
    anakin naboo c3p0,anakin naboo r2d2
    jarjar naboo c3p0,
    leia naboo c3p0,
    obi-wan naboo c3p0,obi-wan naboo r2d2
  """)),
  # nonexistent notebook
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
    b5d7f583fe24ed18083a,jarjar naboo c3p0,
    b0dea5555379c9e3384d,leia naboo c3p0,
    b642fa7c51f517fa4092,obi-wan naboo c3p0,obi-wan naboo r2d2
  """)),
  # no notebook
  ("", None, None, 400, "no notebook specified")
))
@mock.patch("nbforms_server.models.random")
def test_data(mocked_random, client, seed_responses, notebook, questions, user_hashes, want_code, want_body):
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

  # check that output rows were (or in this case would have been) shuffled
  if user_hashes: mocked_random.shuffle.assert_called()
