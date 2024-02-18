"""Database models for an nbforms server"""

import datetime as dt
import hashlib
import random

from argon2 import PasswordHasher
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, select, Sequence
from sqlalchemy import create_engine
from sqlalchemy.orm import (
  DeclarativeBase,
  Mapped,
  mapped_column,
  relationship,
  sessionmaker,
)
from typing import Dict, List, Optional, Tuple, Type, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
  from sqlalchemy.orm import Session as SessionType


class Base(DeclarativeBase):
  pass


db = SQLAlchemy(model_class=Base)
ph = PasswordHasher()
Session = sessionmaker()
T = TypeVar("T")


class User(db.Model):
  """
  A model representing a user.
  """
  __tablename__ = "users"

  id: Mapped[int] = mapped_column(Sequence("user_id_seq"), primary_key=True)
  """the primary key of the table"""

  username: Mapped[str] = mapped_column(unique=True)
  """the user's username"""

  password_hash: Mapped[str] = mapped_column()
  """user's password, hashed with argon2"""

  api_key: Mapped[Optional[str]] = mapped_column(unique=True)
  """the user's most recent API key"""

  no_auth: Mapped[Optional[bool]] = mapped_column()
  """whether this user was created with no auth (meaning it can't be logged into again)"""

  responses: Mapped[List["Response"]] = relationship(back_populates="user", cascade="all, delete-orphan")
  """all responses the user has submitted"""

  attendance_submissions: Mapped[List["AttendanceSubmission"]] = relationship(back_populates="user", cascade="all, delete-orphan")
  """all of the user's attendance submissions"""

  def __repr__(self):
    return f"<User(username={self.username})>"

  @classmethod
  def from_no_auth(cls) -> "User":
    """
    Create a user with a randomly-generated username for no-auth server instances.
    """
    return User(username=f"noauth_{random.randbytes(8).hex()}", password_hash="", no_auth=True)

  @classmethod
  def with_credentials(cls, username: str, password: str) -> "User":
    """
    Create a user with the provided credentials.
    """
    u = User(username=username)
    u.set_password(password)
    return u
  
  @staticmethod
  def header_row() -> List[str]:
    """
    Create a list representing the column headers for the rows returned by ``self.to_row()``.
    """
    return [
      "id",
      "username",
      "no_auth",
    ]

  def to_row(self) -> List:
    """
    Convert this model into a list of its attributes, suitable for rendering into a CSV.
    """
    return [
      self.id,
      self.username,
      self.no_auth or False,
    ]

  def hash_username(self):
    """
    Generate a hash of the user's username, for pseudonymization.
    """
    hashed = hashlib.sha256(self.username.encode()).hexdigest()
    return hashed[:20]

  def set_password(self, pw: str):
    """
    Update the user's password.
    """
    self.password_hash = ph.hash(pw)

  def check_password(self, session: "SessionType", pw: str) -> bool:
    """
    Check if the provided password matches this user's password.

    If the argon2 parameters have changed since the password hash on this ``User`` was calculated,
    the hash is updated and the changed ``User`` is added to the provided db session.
    """
    try:
      matches = ph.verify(self.password_hash, pw)
    except:
      return False
    if matches and ph.check_needs_rehash(self.password_hash):
      self.password_hash = ph.hash(pw)
      session.add(self)
    return matches

  def set_api_key(self):
    """
    Generate and set a new API key.
    """
    self.api_key = random.randbytes(32).hex()


class Notebook(db.Model):
  """
  A model representing a notebook.
  """
  __tablename__ = "notebooks"

  id: Mapped[int] = mapped_column(Sequence("notebook_id_seq"), primary_key=True)
  """the primary key of the table"""

  identifier: Mapped[str] = mapped_column(unique=True)
  """a unique name for the notebook"""

  attendance_open: Mapped[Optional[bool]] = mapped_column()
  """whether attendance on this notebook is currently open"""

  responses: Mapped[List["Response"]] = relationship(back_populates="notebook", cascade="all, delete-orphan")
  """all responses for questions in this notebook"""

  attendance_submissions: Mapped[List["AttendanceSubmission"]] = relationship(back_populates="notebook", cascade="all, delete-orphan")
  """all attendance submissions for this notebook"""

  def __repr__(self):
    return f"<Notebook(identifier={self.identifier})>"
  
  @staticmethod
  def header_row() -> List[str]:
    """
    Create a list representing the column headers for the rows returned by ``self.to_row()``.
    """
    return [
      "id",
      "identifier",
      "attendance_open",
    ]

  def to_row(self) -> List:
    """
    Convert this model into a list of its attributes, suitable for rendering into a CSV.
    """
    return [
      self.id,
      self.identifier,
      self.attendance_open or False,
    ]


class Response(db.Model):
  """
  A model representing a user's response to a question in a notebook.
  """
  __tablename__ = "responses"

  id: Mapped[int] = mapped_column(Sequence("response_id_seq"), primary_key=True)
  """the primary key of the table"""

  user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
  """the ID of the user this response belongs to"""

  notebook_id: Mapped[int] = mapped_column(ForeignKey("notebooks.id"))
  """the ID of the notebook this response belongs to"""

  question_identifier: Mapped[str] = mapped_column()
  """the identifier of the question this response is for"""

  response: Mapped[str] = mapped_column()
  """the user's response"""

  timestamp: Mapped[dt.datetime] = mapped_column()
  """the timestamp at which this response was written"""

  user: Mapped[User] = relationship(back_populates="responses")
  """the user this response belongs to"""

  notebook: Mapped[Notebook] = relationship(back_populates="responses")
  """the notebook this response belongs to"""


class AttendanceSubmission(db.Model):
  """
  A model representing a user's attendance submission for a notebook.
  """
  __tablename__ = "attendance_submissions"

  id: Mapped[int] = mapped_column(Sequence("attendance_submission_id_seq"), primary_key=True)
  """the primary key of the table"""

  user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
  """the ID of the user this submission belongs to"""

  notebook_id: Mapped[int] = mapped_column(ForeignKey("notebooks.id"))
  """the ID of the notebook this submission belongs to"""

  timestamp: Mapped[dt.datetime] = mapped_column()
  """the timestamp at which this submission was received"""

  was_open: Mapped[bool] = mapped_column()
  """whether the notebook's attendance was open when this submission was received"""

  user: Mapped[User] = relationship(back_populates="attendance_submissions")
  """the user this submission belongs to"""

  notebook: Mapped[Notebook] = relationship(back_populates="attendance_submissions")
  """the notebook this submission belongs to"""

  @staticmethod
  def header_row() -> List[str]:
    """
    Create a list representing the column headers for the rows returned by ``self.to_row()``.
    """
    return [
      "id",
      "user id",
      "username",
      "notebook",
      "timestamp",
      "was_open",
    ]

  def to_row(self) -> List:
    """
    Convert this model into a list of its attributes, suitable for rendering into a CSV.
    """
    return [
      self.id,
      self.user_id,
      self.user.username,
      self.notebook.identifier,
      str(self.timestamp),
      self.was_open,
    ]


def get_or_create(session: "SessionType", model: Type[T], **kwargs) -> T:
  """
  Find an instance of a model class in the database using the filters in ``kwargs`` or create one
  if no such row exists. If the row is created, it is also added to the provided session.
  """
  instance = session.query(model).filter_by(**kwargs).first()
  if instance:
    return instance
  else:
    instance = model(**kwargs)
    session.add(instance)
    return instance


def export_responses(
  session: "SessionType",
  notebook: Notebook,
  req_questions: List[str],
  *,
  user_hashes: bool = False,
  usernames: bool = False,
) -> Tuple[List[List[str]], Optional[str]]:
  """
  Export responses for questions in the specified notebook to a 2D list. If ``req_questions`` is
  empty, no question filtering is applied. Usernames or pseudonymized usernames can be included by
  setting ``usernames`` or ``user_hashes`` to true, resp.
  """
  # query for all responses matching the notebook and requested questions
  stmt = select(Response).where(Response.notebook == notebook)
  if req_questions:
    stmt = stmt.where(Response.question_identifier.in_(req_questions))

  responses = session.scalars(stmt).all()
  if len(responses) == 0:
    return [], "no responses found"

  # TODO: this impl doesn't ensure that the latest response is used

  # group responses by user and question
  questions = set()
  by_user_and_question: Dict[int, Dict[str, Response]] = {}
  users_by_username: Dict[str, User] = {}
  for r in responses:
    questions.add(r.question_identifier)
    if r.user_id not in by_user_and_question:
      by_user_and_question[r.user_id] = {}
    by_user_and_question[r.user_id][r.question_identifier] = r
    users_by_username[r.user.username] = r.user

  # ensure there is a column for every requested question
  for q in req_questions:
    questions.add(q)

  questions = sorted(questions)

  rows = [(["user"] if user_hashes or usernames else []) + questions]
  for un in sorted(users_by_username.keys()):
    u = users_by_username[un]
    row = []
    if user_hashes:
      row.append(u.hash_username())
    elif usernames:
      row.append(u.username)

    # append the user's response to each question to the row
    user_res = by_user_and_question[u.id]
    for q in questions:
      res = ""
      if q in user_res:
        res = user_res[q].response
      row.append(res)

    rows.append(row)

  # if pseudonymization is enabled, randomize the ordering of the returned rows so as not to leak
  # any information, since by default the rows are sorted by username
  if user_hashes:
    shuffled_rows = rows[1:]
    random.shuffle(shuffled_rows)
    rows = [rows[0]] + shuffled_rows

  return rows, None
