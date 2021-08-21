import datetime
import os.path
import sqlite3
from typing import Optional

from appdirs import user_data_dir

from . import constants

USER_DATA_DIR = user_data_dir(constants.APP_NAME, constants.AUTHOR_NAME)
DB_PATH = os.path.join(USER_DATA_DIR, "dejima.db")


class Connection:
    _db: sqlite3.Connection

    def __init__(self):
        if not os.path.exists(USER_DATA_DIR):
            os.makedirs(USER_DATA_DIR, exist_ok=True)

        self._db = sqlite3.Connection(
            DB_PATH,
            detect_types=sqlite3.PARSE_DECLTYPES,
            isolation_level=None,
        )

        self._create_tables()

        super().__init__()

    def get_cursor(self) -> sqlite3.Cursor:
        return self._db.cursor()

    def _create_tables(self):
        cursor = self.get_cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS known_entries (
                key string,
                source string,
                anki_id integer,
                importName string,
                imported timestamp
            )
        """
        )
        cursor.close()

    def mark_entry_processed(
        self, source: str, key: str, anki_id: Optional[int], import_name: str
    ):
        cursor = self.get_cursor()
        cursor.execute(
            """
            INSERT INTO known_entries
                (key, source, anki_id, imported, importName)
            VALUES
                (?, ?, ?, ?, ?)
        """,
            (key, source, anki_id, datetime.datetime.utcnow(), import_name),
        )
        cursor.close()

    def annotation_is_known(self, source: str, key: str) -> bool:
        cursor = self.get_cursor()
        cursor.execute(
            """
            SELECT 1
            FROM known_entries
            WHERE key = ? AND source = ?
        """,
            (
                key,
                source,
            ),
        )

        exists = len(cursor.fetchall()) > 0
        cursor.close()

        return exists
