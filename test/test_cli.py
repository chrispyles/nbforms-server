"""Tests for the nbforms server CLI"""

import click
import datetime as dt
import pytest
import runpy
import sys

from click.testing import CliRunner, Result
from textwrap import dedent
from unittest import mock

from nbforms_server.models import AttendanceSubmission, db, Notebook, Response, User


def assert_cli_result(result: Result, expect_error, want_stdout=None, want_exc=None):
  """
  Asserts that the ``CliRunner`` result exited with the correct code, stdout, and exception.
  """
  assert (
    result.exit_code != 0
    if expect_error
    else result.exit_code == 0
  ), result.stdout or result.exception

  if want_stdout is not None:
    assert result.stdout == want_stdout

  if want_exc is not None:
    assert isinstance(result.exception, type(want_exc))
    assert str(result.exception) == str(want_exc)


@pytest.fixture
def run_cli():
  """
  A fixture that provides a function to run the CLI on a list of arguments.
  """
  from nbforms_server.__main__ import cli
  runner = CliRunner()
  with runner.isolated_filesystem():
    yield lambda cmd, input=None: runner.invoke(cli, cmd, input=input)


@mock.patch.object(click, "group")
def test_cli_launch(mocked_group):
  """Test that running ``nbforms_server`` as a module invokes the click CLI."""
  runpy.run_module("nbforms_server", run_name="__main__")

  # this checks that ``nbforms.__main__.cli`` was called, since it is decorated with
  # ``click.group()`` (making it the return value of the return value of ``mocked_group``)
  mocked_group.return_value.return_value.assert_called()


class TestAttendance:
  """Tests for the ``attendance`` group."""

  @pytest.mark.parametrize(("args", "want_error", "want_stdout", "want_exc"), (
    # no notebook identifier should error
    ([], True, None, None),
    # nonexistent notebook identifier should error
    (["mustafar"], True, None, ValueError("No such notebook: mustafar")),
    # nonexistent notebook with --create should work
    (["mustafar", "--create"], False, "", None),
    # existing notebook
    (["naboo"], False, "", None),
  ))
  def test_open(self, app, run_cli, seed_data, args, want_error, want_stdout, want_exc):
    """Test the ``attendance open`` command."""
    res = run_cli(["attendance", "open"] + args)
    assert_cli_result(res, want_error, want_stdout, want_exc)

    if want_error: return

    with app.app_context():
      nb = db.session.query(Notebook).filter_by(identifier=args[0]).first()

    assert nb.attendance_open is True

  @pytest.mark.parametrize(("args", "want_error", "want_stdout", "want_exc"), (
    # no notebook identifier should error
    ([], True, None, None),
    # nonexistent notebook identifier should error
    (["mustafar"], True, None, ValueError("No such notebook: mustafar")),
    # nonexistent notebook with --create should work
    (["mustafar", "--create"], False, "", None),
    # existing notebook not open
    (["naboo"], False, "", None),
    # existing notebook open
    (["coruscant"], False, "", None),
  ))
  def test_close(self, app, run_cli, seed_data, args, want_error, want_stdout, want_exc):
    """Test the ``attendance close`` command."""
    res = run_cli(["attendance", "close"] + args)
    assert_cli_result(res, want_error, want_stdout, want_exc)

    if want_error: return

    with app.app_context():
      nb = db.session.query(Notebook).filter_by(identifier=args[0]).first()

    assert nb.attendance_open is False


class TestClear:
  """Tests for the ``clear`` group."""

  @pytest.mark.parametrize(("force", "confirm", "want_clear"), (
    (False, "", False),
    (False, "n", False),
    (False, "y", True),
    (False, "Y", True),
    (True, None, True),
  ))
  def test_all(
    self,
    app,
    run_cli,
    seed_data,
    seed_responses,
    seed_attendance_submissions,
    force,
    confirm,
    want_clear,
  ):
    """Test the ``clear all`` command."""

    res = run_cli(["clear", "all"] + (["--force"] if force else []), input=confirm)
    assert_cli_result(res, False, None, None)

    with app.app_context():
      assert len(db.session.query(Response).all()) == (0 if want_clear else 9)
      assert len(db.session.query(AttendanceSubmission).all()) == (0 if want_clear else 4)

  @pytest.mark.parametrize(("username", "force", "confirm", "want_clear", "want_exc"), (
    ("anakin", False, "", False, None),
    ("anakin", False, "n", False, None),
    ("anakin", False, "y", True, None),
    ("anakin", False, "Y", True, None),
    ("anakin", True, None, True, None),
    # nonexistent user
    ("han", False, "y", False, ValueError("No such user: han")),
  ))
  def test_user(
    self,
    app,
    run_cli,
    seed_responses,
    seed_attendance_submissions,
    username,
    force,
    confirm,
    want_clear,
    want_exc,
  ):
    """Test the ``clear user`` command."""
    with app.app_context():
      seed_usernames = [u.username for u in db.session.query(User).all()]

    res = run_cli(["clear", "user", username] + (["--force"] if force else []), input=confirm)
    assert_cli_result(res, username not in seed_usernames, None, want_exc)

    if username in seed_usernames:
      with app.app_context():
        res, sub = (
          db.session.query(Response).join(User).filter(User.username == username).all(),
          db.session.query(AttendanceSubmission).join(User).filter(User.username == username).all(),
        )
        assert len(res) == (0 if want_clear else 3)
        assert len(sub) == (0 if want_clear else 1)

  @pytest.mark.parametrize(("notebook", "force", "confirm", "want_clear", "want_exc"), (
    ("naboo", False, "", False, None),
    ("naboo", False, "n", False, None),
    ("naboo", False, "y", True, None),
    ("naboo", False, "Y", True, None),
    ("naboo", True, None, True, None),
    # nonexistent notebook
    ("mustafar", False, "y", False, ValueError("No such notebook: mustafar")),
  ))
  def test_notebook(
    self,
    app,
    run_cli,
    seed_responses,
    seed_attendance_submissions,
    notebook,
    force,
    confirm,
    want_clear,
    want_exc,
  ):
    """Test the ``clear notebook`` command."""
    with app.app_context():
      seed_notebooks = [n.identifier for n in db.session.query(Notebook).all()]

    res = run_cli(["clear", "notebook", notebook] + (["--force"] if force else []), input=confirm)
    assert_cli_result(res, notebook not in seed_notebooks, None, want_exc)

    if notebook in seed_notebooks:
      with app.app_context():
        res, sub = (
          db.session.query(Response).join(Notebook).filter(Notebook.identifier == notebook).all(),
          db.session.query(AttendanceSubmission).join(Notebook).filter(Notebook.identifier == notebook).all(),
        )
        assert len(res) == (0 if want_clear else 6)
        assert len(sub) == (0 if want_clear else 4)


class TestReports:
  """Tests for the ``reports`` group."""

  @pytest.mark.parametrize(("dest", "want_csv_stdout"), (
    (None, True),
    ("out.csv", False),
  ))
  def test_users(self, run_cli, seed_data, dest, want_csv_stdout):
    """Test the ``reports users`` command."""
    want_csv = dedent("""\
      id,username,no_auth
      1,anakin,False
      3,jarjar,False
      4,leia,False
      5,noauth_han,True
      2,obi-wan,False
    """)

    res = run_cli(["reports", "users"] + ([dest] if dest is not None else []))
    assert_cli_result(res, False, "", None)

    if want_csv_stdout:
      sys.stdout.read() == want_csv
    else:
      with open(dest) as f:
        assert f.read() == want_csv

  @pytest.mark.parametrize(("dest", "want_csv_stdout"), (
    (None, True),
    ("out.csv", False),
  ))
  def test_notebooks(self, run_cli, seed_data, dest, want_csv_stdout):
    """Test the ``reports notebooks`` command."""
    want_csv = dedent("""\
      id,identifier,attendance_open
      2,coruscant,True
      1,naboo,False
      3,tatooine,False
    """)

    res = run_cli(["reports", "notebooks"] + ([dest] if dest is not None else []))
    assert_cli_result(res, False, "", None)

    if want_csv_stdout:
      sys.stdout.read() == want_csv
    else:
      with open(dest) as f:
        assert f.read() == want_csv

  @pytest.mark.parametrize(("notebook", "dest", "want_error", "want_csv_stdout", "want_exc"), (
    # no notebook should error
    ("", None, True, None, None),
    ("naboo", None, False, True, None),
    ("naboo", "out.csv", False, False, None),
    # nonexistent notebook
    ("mustafar", None, True, None, ValueError("No such notebook: mustafar")),
    # notebook with no responses
    ("tatooine", None, True, None, ValueError("no responses found")),
  ))
  def test_responses(self, run_cli, seed_responses, notebook, dest, want_error, want_csv_stdout, want_exc):
    """Test the ``reports responses`` command."""
    want_csv = dedent("""\
      user,c3p0,r2d2
      anakin,anakin naboo c3p0,anakin naboo r2d2
      jarjar,jarjar naboo c3p0,
      leia,leia naboo c3p0,
      obi-wan,obi-wan naboo c3p0,obi-wan naboo r2d2
    """)

    res = run_cli(["reports", "responses", notebook] + ([dest] if dest is not None else []))
    assert_cli_result(res, want_error, "", want_exc)

    if want_csv_stdout:
      sys.stdout.read() == want_csv
    elif not want_error:
      with open(dest) as f:
        assert f.read() == want_csv

  @pytest.mark.parametrize(("notebook", "dest", "want_error", "want_csv_stdout", "want_exc"), (
    # no notebook should error
    ("", None, True, None, None),
    ("naboo", None, False, True, None),
    ("naboo", "out.csv", False, False, None),
    # nonexistent notebook
    ("mustafar", None, True, None, ValueError("No such notebook: mustafar")),
  ))
  def test_attendance(self, run_cli, seed_attendance_submissions, notebook, dest, want_error, want_csv_stdout, want_exc):
    """Test the ``reports attendance`` command."""
    want_csv = dedent(f"""\
      id,user id,username,notebook,timestamp,was_open
      1,1,anakin,naboo,{dt.datetime(2024, 2, 11, 12, 23, 57)},False
      3,3,jarjar,naboo,{dt.datetime(2024, 2, 11, 13, 23, 57)},True
      4,4,leia,naboo,{dt.datetime(2024, 2, 11, 14, 23, 57)},False
      2,2,obi-wan,naboo,{dt.datetime(2024, 2, 11, 13, 23, 57)},True
    """)

    res = run_cli(["reports", "attendance", notebook] + ([dest] if dest is not None else []))
    assert_cli_result(res, want_error, "", want_exc)

    if want_csv_stdout:
      sys.stdout.read() == want_csv
    elif not want_error:
      with open(dest) as f:
        assert f.read() == want_csv


@pytest.mark.parametrize(("csv", "want_error", "want_exc"), (
  # no csv file should error
  (None, True, None),
  # valid csv
  ("username,password\nanakin,skywalker\nobi-wan,kenobi\njarjar,binks\n", False, None),
  # incorrect headers
  ("password,username\nanakin,skywalker\nobi-wan,kenobi\njarjar,binks\n", True, ValueError("CSV file does not contain expected headers; the columns should be 'username' and 'password' (in that order)")),
  # wrong no. of columns in a row
  ("username,password\nanakin,skywalker\nobi-wan\njarjar,binks\n", True, ValueError("Row 3 does not have 2 columns")),
  ("username,password\nanakin,skywalker\nobi-wan,kenobi,jedi\njarjar,binks\n", True, ValueError("Row 3 does not have 2 columns")),
))
@mock.patch("nbforms_server.models.ph")
def test_seed(mocked_ph, app, run_cli, csv, want_error, want_exc):
  """Test the ``seed`` command."""
  count = 0
  def incr(*args):
    nonlocal count
    count += 1
    return str(count)

  mocked_ph.hash.side_effect = incr

  if csv is not None:
    with open("users.csv", "w+") as f:
      f.write(csv)

  res = run_cli(["seed"] + (["users.csv"] if csv is not None else []))
  assert_cli_result(res, want_error, "Successfully import 3 users\n" if not want_error else None, want_exc)

  want_users = [
    {
      "username": "anakin",
      "password_hash": "1",
    },
    {
      "username": "obi-wan",
      "password_hash": "2",
    },
    {
      "username": "jarjar",
      "password_hash": "3",
    },
  ]

  with app.app_context():
    users = db.session.query(User).all()

    if want_error:
      assert len(users) == 0
    else:
      assert len(users) == len(want_users)
      for i, (u, wu) in enumerate(zip(users, want_users)):
        for k, v in wu.items():
          assert getattr(u, k) == v, f"wrong value for attribute '{k}' in user {i}"
