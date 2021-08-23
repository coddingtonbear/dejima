import json
from unittest import TestCase
from unittest.mock import ANY
from unittest.mock import Mock
from unittest.mock import patch

import pytest
import requests

from ..api import AnkiError
from ..api import Connection


class TestApi(TestCase):
    def setUp(self):
        self.response_data = {
            "result": None,
            "error": None,
        }
        self.response = Mock(
            json=Mock(
                return_value=self.response_data,
            ),
            spec=requests.Response,
        )

        with patch("requests.Session") as session:
            session.return_value = Mock(post=Mock(return_value=self.response))

            self.session = session

            self.api = Connection()

    def test_dispatch(self):
        arbitrary_action = "some_action"
        arbitrary_params = {
            "something": "special",
        }

        self.api._dispatch(arbitrary_action, arbitrary_params)

        self.session.return_value.post.assert_called_with(
            ANY,
            data=json.dumps(
                {"action": arbitrary_action, "version": 6, "params": arbitrary_params},
                indent=4,
                sort_keys=True,
            ),
        )

    def test_dispatch_no_parms(self):
        arbitrary_action = "some_action"

        self.api._dispatch(arbitrary_action)

        self.session.return_value.post.assert_called_with(
            ANY,
            data=json.dumps(
                {"action": arbitrary_action, "version": 6},
                indent=4,
                sort_keys=True,
            ),
        )

    def test_dispatch_error(self):
        arbitrary_action = "some_action"
        arbitrary_error_msg = "some error"

        self.response_data["error"] = arbitrary_error_msg

        with pytest.raises(AnkiError):
            self.api._dispatch(arbitrary_action)
