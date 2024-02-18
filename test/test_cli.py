"""Tests for the nbforms server CLI"""

import pytest

from click.testing import CliRunner, Result

from nbforms_server.__main__ import cli
from nbforms_server.models import AttendanceSubmission, db, Notebook, Response


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
