"""Tests for ``nbforms_server.utils``"""

from nbforms_server.utils import get_db_path


def test_get_db_path(app):
  """Test ``nbforms_server.utils.get_db_path``."""
  assert get_db_path(app) == f"{app.instance_path}/nbforms_server.db"
