"""A CLI for managing an nbforms server"""

import click
import csv
import sys

from sqlalchemy import create_engine, select
from typing import IO, TYPE_CHECKING

from . import create_app
from .models import (
  AttendanceSubmission,
  db,
  export_responses,
  get_or_create,
  Notebook,
  Response,
  User,
)
from .utils import to_csv

if TYPE_CHECKING:
  from flask import Flask
  from sqlalchemy.orm import Session as SessionType


class Context:
  """
  A context object for managing things like the DB connection in the CLI.
  """

  debug: bool
  """whether debug mode is enabled"""

  app: "Flask"

  session: "SessionType"
  """the sqlalchemy DB session"""

  def __init__(self, debug: bool):
    self.debug = debug
    self.app = create_app()

  def maybe_get_or_create_notebook(self, identifier: str, create: bool):
    """
    Like ``get_or_create`` for a ``Notebook``, but it will only create the instance of ``create`` is
    true (otherwise it throws a ``ValueError`` if the instance is not found in the DB).
    """
    with self.app.app_context():
      if create:
        return get_or_create(db.session, Notebook, identifier=identifier)
      else:
        nb = db.session.query(Notebook).filter_by(identifier=identifier).first()
        if not nb:
          raise ValueError(f"No such notebook: {identifier}")
        return nb


@click.group()
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.pass_context
def cli(click_ctx: click.Context, debug: bool):
  click_ctx.obj = Context(debug)


@cli.group("attendance")
def attendance():
  """
  Manage attendance tracking for notebooks.
  """
  pass


@attendance.command("open")
@click.argument("notebook", required=True)
@click.option("--create", is_flag=True, help="Create the notebook if it does not exist")
@click.pass_obj
def attendance_open(ctx: Context, notebook: str, create: bool):
  """
  Open attendance for the notebook with identifier NOTEBOOK.
  """
  with ctx.app.app_context():
    nb = ctx.maybe_get_or_create_notebook(notebook, create)
    nb.attendance_open = True
    db.session.add(nb)
    db.session.commit()


@attendance.command("close")
@click.argument("notebook", required=True)
@click.option("--create", is_flag=True, help="Create the notebook if it does not exist")
@click.pass_obj
def attendance_close(ctx: Context, notebook: str, create: bool):
  """
  Close attendance for the notebook with identifier NOTEBOOK.
  """
  with ctx.app.app_context():
    nb = ctx.maybe_get_or_create_notebook(notebook, create)
    nb.attendance_open = False
    db.session.add(nb)
    db.session.commit()


@cli.group("clear")
def clear():
  """
  Clear subsets of data from the database.
  """
  pass


@clear.command("all")
@click.option("--force", is_flag=True, help="Do not ask for confirmation before deleting")
@click.pass_obj
def clear_all(ctx: Context, force: bool):
  """
  Clear all response and attendance submission entries in the database.
  """
  if not force:
    if not click.confirm("Are you sure you want to delete everything?"):
      click.echo("clear all aborted")
      return

  with ctx.app.app_context():
    db.session.query(Response).delete()
    db.session.query(AttendanceSubmission).delete()
    db.session.commit()


@clear.command("user")
@click.argument("username")
@click.option("--force", is_flag=True, help="Do not ask for confirmation before deleting")
@click.pass_obj
def clear_all(ctx: Context, username: str, force: bool):
  """
  Clear all response and attendance submission entries for the user with username USERNAME.
  """
  if not force:
    if not click.confirm("Are you sure you want to delete this user's data?"):
      click.echo("clear user aborted")
      return

  with ctx.app.app_context():
    u = db.session.query(User).filter_by(username=username).first()
    if not u:
      raise ValueError(f"No such user: {username}")

    db.session.query(Response).filter_by(user=u).delete()
    db.session.query(AttendanceSubmission).filter_by(user=u).delete()
    db.session.commit()


@clear.command("notebook")
@click.argument("notebook")
@click.option("--force", is_flag=True, help="Do not ask for confirmation before deleting")
@click.pass_obj
def clear_all(ctx: Context, notebook: str, force: bool):
  """
  Clear all response and attendance submission entries for the notebook with identifier NOTEBOOK.
  """
  if not force:
    if not click.confirm("Are you sure you want to delete this notebook's data?"):
      click.echo("clear notebook aborted")
      return

  with ctx.app.app_context():
    nb = ctx.maybe_get_or_create_notebook(notebook, False)
    db.session.query(Response).filter_by(notebook=nb).delete()
    db.session.query(AttendanceSubmission).filter_by(notebook=nb).delete()
    db.session.commit()


@cli.group("reports")
def reports():
  """
  Generate reports from the database.
  """
  pass


@reports.command("users")
@click.argument("dest", type=click.File("w"), default=sys.stdout)
@click.pass_obj
def reports_users(ctx: Context, dest: IO):
  """
  Generate a CSV report of all users in the database and write it to DEST (or stdout if DEST is
  unsepcified).
  """
  with ctx.app.app_context():
    users = db.session.query(User).order_by(User.username).all()
    csv = to_csv([User.header_row(), *(u.to_row() for u in users)])

  dest.write(csv)


@reports.command("notebooks")
@click.argument("dest", type=click.File("w"), default=sys.stdout)
@click.pass_obj
def reports_notebooks(ctx: Context, dest: IO):
  """
  Generate a CSV report of all notebooks in the database and write it to DEST (or stdout if DEST is
  unsepcified).
  """
  with ctx.app.app_context():
    nbs = db.session.query(Notebook).order_by(Notebook.identifier).all()
    csv = to_csv([Notebook.header_row(), *(nb.to_row() for nb in nbs)])

  dest.write(csv)


@reports.command("responses")
@click.argument("notebook", required=True)
@click.argument("dest", type=click.File("w"), default=sys.stdout)
@click.pass_obj
def reports_responses(ctx: Context, notebook: str, dest: IO):
  """
  Generate a CSV report of all responses to notebook with identifier NOTEBOOK and write it to
  DEST (or stdout if DEST is unsepcified).
  """
  with ctx.app.app_context():
    nb = ctx.maybe_get_or_create_notebook(notebook, False)
    rows, err = export_responses(db.session, nb, [], usernames=True)

  if err:
    raise ValueError(err)

  dest.write(to_csv(rows))


@reports.command("attendance")
@click.argument("notebook", required=True)
@click.argument("dest", type=click.File("w"), default=sys.stdout)
@click.pass_obj
def attendance_report(ctx: Context, notebook: str, dest: IO):
  """
  Generate a CSV report of attendance submissions for notebook identifier NOTEBOOK and write it to
  DEST (or stdout if DEST is unsepcified).
  """
  with ctx.app.app_context():
    nb = ctx.maybe_get_or_create_notebook(notebook, False)
    subms = db.session.query(AttendanceSubmission).filter_by(notebook=nb).join(User).order_by(User.username).all()
    csv = to_csv([AttendanceSubmission.header_row(), *(s.to_row() for s in subms)])

  dest.write(csv)


@cli.command("seed")
@click.argument("file", type=click.File())
@click.pass_obj
def seed(ctx: Context, file: IO):
  """
  Seed the users table with users from the CSV file FILE.

  The CSV file must be formatted as below (the column ordering is required):

  \b
  username,password
  u1,p1
  u2,p2
  # etc.
  """
  rows = list(csv.reader(file))
  if rows[0] != ["username", "password"]:
    raise ValueError("CSV file does not contain expected headers; the columns should be 'username' and 'password' (in that order)")

  with ctx.app.app_context():
    for i, r in enumerate(rows[1:]):
      if len(r) != 2:
        raise ValueError(f"Row {i + 2} does not have 2 columns")

      u = User.with_credentials(*r)
      db.session.add(u)

    db.session.commit()

  click.echo(f"Successfully import {len(rows) - 1} users")


if __name__ == "__main__":
  cli()
