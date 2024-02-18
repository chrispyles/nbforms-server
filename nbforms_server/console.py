"""A console for interacting with the nbforms server database"""

from sqlalchemy import create_engine

from . import create_app
from .models import *
from .utils import get_db_path


if __name__ == "__main__":
  app = create_app()
  engine = create_engine(f"sqlite:///{get_db_path(app)}")
  Session.configure(bind=engine)
  session = Session()
