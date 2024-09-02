from pathlib import Path

from .utils import initial_db

db_path: Path = Path(__file__).parent.parent / "observe.db"
db_path.unlink(missing_ok=True)
initial_db(db_path=db_path)
