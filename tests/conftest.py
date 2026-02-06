import sys
import pytest
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass


@pytest.fixture(scope="session")
def test_user_id():
    return "user_test"


@pytest.fixture(scope="session")
def test_leo_user_id():
    return "user_leo"


@pytest.fixture(scope="session")
def test_luiz_user_id():
    return "user_luiz"
