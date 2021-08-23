import shutil
import tempfile
import uuid
from unittest import TestCase
from unittest.mock import patch

from ..db import Connection


class TestDbConnection(TestCase):
    def setUp(self):
        self._tmp_dir = tempfile.mkdtemp()

        with patch("appdirs.user_data_dir") as user_data_dir:
            user_data_dir.return_value = self._tmp_dir
            self.db = Connection()

        super().setUp()

    def tearDown(self) -> None:
        shutil.rmtree(self._tmp_dir)
        return super().tearDown()

    def test_mark_entry_processed(self):
        arbitrary_source = "arbitrary source"
        arbitrary_key = str(uuid.uuid4())

        self.db.mark_entry_processed(
            arbitrary_source,
            arbitrary_key,
            10384134,
            "arbitrary import name",
        )

        actual_result = self.db.annotation_is_known(
            arbitrary_source,
            arbitrary_key,
        )
        expected_result = True

        assert actual_result == expected_result

    def test_mark_entry_processed_no_id(self):
        arbitrary_source = "arbitrary source"
        arbitrary_key = str(uuid.uuid4())

        self.db.mark_entry_processed(
            arbitrary_source,
            arbitrary_key,
            None,
            "arbitrary import name",
        )

        actual_result = self.db.annotation_is_known(
            arbitrary_source,
            arbitrary_key,
        )
        expected_result = True

        assert actual_result == expected_result

    def test_annotation_is_known_but_its_not(self):
        arbitrary_source = "arbitrary source"
        arbitrary_key = str(uuid.uuid4())

        actual_result = self.db.annotation_is_known(
            arbitrary_source,
            arbitrary_key,
        )
        expected_result = False

        assert actual_result == expected_result
