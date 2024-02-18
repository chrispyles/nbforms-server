"""Tests for the nbforms server CLI"""

import pytest

from click.testing import CliRunner, Result

from nbforms_server.__main__ import cli
from nbforms_server.models import AttendanceSubmission, db, Notebook, Response, User


def assert_cli_result(result: Result, expect_error, want_stdout=None, want_exc=None):
  """
  Asserts that the ``CliRunner`` result exited with the correct code, stdout, and exception.
  """
  assert (
    result.exit_code != 0
    if expect_error
    else result.exit_code == 0
  ), result.stdout

  if want_stdout is not None:
    assert result.stdout == want_stdout

  if want_exc is not None:
    assert isinstance(result.exception, type(want_exc))
    assert str(result.exception) == str(want_exc)


@pytest.fixture()
def run_cli():
  """
  A fixture that provides a function to run the CLI on a list of arguments.
  """
  runner = CliRunner()
  with runner.isolated_filesystem():
    yield lambda cmd, input=None: runner.invoke(cli, cmd, input=input)


class TestAttendance:
  """Tests for the ``attendance`` group."""

  @pytest.mark.parametrize(("args", "want_error", "want_stdout", "want_exc"), (
    # no notebook identifier should error
    ([], True, None, None),
    # nonexistant notebook identifier should error
    (["mustafar"], True, None, ValueError("No such notebook: mustafar")),
    # nonexistant notebook with --create should work
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
    # nonexistant notebook identifier should error
    (["mustafar"], True, None, ValueError("No such notebook: mustafar")),
    # nonexistant notebook with --create should work
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
    # nonexistant user
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
    # nonexistant notebook
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
