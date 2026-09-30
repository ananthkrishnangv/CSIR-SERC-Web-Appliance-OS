import sys
import os
from pathlib import Path

backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

# Use isolated test database file
test_db_path = backend_path / "data" / "test_swa.db"
os.environ["DATABASE_URL"] = f"sqlite:///{test_db_path}"
