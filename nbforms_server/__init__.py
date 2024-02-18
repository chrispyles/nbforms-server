"""A simple flask server for collecting data from nbforms clients"""

import datetime as dt
import os

from flask import Flask, render_template, request, Response as FlaskResponse

from .models import (
  AttendanceSubmission,
  db,
  export_responses,
  get_or_create,
  Notebook,
  Response,
  User,
)
from .utils import DB_FILENAME, to_csv


def create_app(config=None) -> Flask:
  """
  Create the Flask app for the nbforms server.
  """
  app = Flask(__name__)
  app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_FILENAME}"
  if config:
    app.config.from_mapping(config)

  os.makedirs(app.instance_path, exist_ok=True)

  db.init_app(app)

  with app.app_context():
    db.create_all()

  @app.route("/")
  def index():
    """
    Render the homepage.
    """
    return render_template("index.html")

  @app.post("/auth")
  def auth():
    """
    Authenticate a user, then generate and return a new API key for them.
    """
    if os.environ.get("NBFORMS_SERVER_NO_AUTH_REQUIRED", "false") == "true":
      user = User()
      user.set_api_key()
      db.session.add(user)

    else:
      body = request.get_json()
      for k in ["username", "password"]:
        if not body.get(k):
          return f"no {k} specified", 400

      user = get_or_create(db.session, User, username=body.get("username"))
      if user.password_hash is None:
        user.set_password(body.get("password"))
        user.set_api_key()
        db.session.add(user)

      elif user.check_password(db.session, body.get("password")):
        user.set_api_key()
        db.session.add(user)

      else:
        return "invalid login", 400
    
    db.session.commit()
    return user.api_key

  # Expects a body of the format:
  #   {
  #     "api_key": "",
  #     "notebook": "",
  #     "responses": [
  #       {
  #         "identifier": "q1",
  #         "response": "foo",
  #       },
  #     ],
  #   }
  @app.post("/submit")
  def submit():
    """
    Write a user's responses to questions in a notebook to the DB.
    """
    body = request.get_json(force=True)
    for k in ["api_key", "notebook", "responses"]:
      if not body.get(k):
        return f"no {k} specified", 400

    user = db.session.query(User).filter_by(api_key=body.get("api_key")).first()
    if user is None:
      return "no such user", 400

    notebook = get_or_create(db.session, Notebook, identifier=body.get("notebook"))

    for res in body.get("responses"):
      if "identifier" not in res:
        return f"invalid response: {res}", 400
      response = get_or_create(db.session, Response, user=user, notebook=notebook, question_identifier=res["identifier"])
      response.response = str(res.get("response", ""))
      response.timestamp = dt.datetime.now()
      db.session.add(response)

    db.session.commit()
    return "ok"

  @app.post("/attendance")
  def attendance():
    """
    Record a user's attendance for a notebook.
    """
    body = request.get_json()
    for k in ["api_key", "notebook"]:
      if not body.get(k):
        return f"no {k} specified", 400

    user = db.session.query(User).filter_by(api_key=body.get("api_key")).first()
    if user is None:
      return "no such user", 400

    notebook = get_or_create(db.session, Notebook, identifier=body.get("notebook"))

    subm = AttendanceSubmission(
      user = user,
      notebook = notebook,
      timestamp = dt.datetime.now(),
      was_open = notebook.attendance_open or False,
    )
    db.session.add(subm)

    db.session.commit()
    return "ok"

  @app.get("/data")
  def data():
    """
    Return question responses for a notebook in CSV format.
    """
    body = request.get_json()
    if not body.get("notebook"):
      return f"no notebook specified", 400

    questions = body.get("questions", [])
    notebook = get_or_create(db.session, Notebook, identifier=body.get("notebook"))
    user_hashes = body.get("user_hashes", False)

    rows, err = export_responses(db.session, notebook, questions, user_hashes=user_hashes)
    if err:
      return err, 400

    db.session.commit()
    return FlaskResponse(to_csv(rows), mimetype="text/csv")

  return app
