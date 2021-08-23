from unittest import TestCase
from unittest.mock import Mock

from .. import plugin


class TestSourcePluginMetaclass(TestCase):
    def test_basic(self):
        class MySource(plugin.SourcePlugin):
            Front = plugin.NoteField()

        source = MySource("arbitrary", Mock(), Mock())

        assert source.Front._attribute_name == "Front"
        assert source._fields
