from __future__ import annotations

import argparse
import dataclasses
import logging
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type

from rich.console import Console
from safdie import BaseCommand
from safdie import get_entrypoints

from .constants import SOURCE_ENTRYPOINT_NAME

logger = logging.getLogger(__name__)


def get_installed_sources() -> Dict[str, Type[SourcePlugin]]:
    return get_entrypoints(SOURCE_ENTRYPOINT_NAME, SourcePlugin)


class NoteField:
    _unique: bool
    _attribute_name: str
    _field_name_override: Optional[str]
    _default: Optional[str]
    _merge: bool
    _optional: bool

    def __init__(
        self,
        field_name: Optional[str] = None,
        unique: bool = False,
        default: str = "",
        merge: bool = False,
        optional: bool = False,
    ):
        if field_name is not None and not field_name:
            raise ValueError("Specified field name is not valid.")

        self._unique = unique
        self._field_name_override = field_name
        self._default = default
        self._merge = merge
        self._optional = optional

        super().__init__()

    def _set_attribute_name(self, value: str) -> None:
        self._attribute_name = value

    @property
    def field_name(self) -> str:
        if self._field_name_override:
            return self._field_name_override

        return self._attribute_name

    @property
    def optional(self) -> bool:
        return self._optional

    @property
    def unique(self) -> bool:
        return self._unique

    @property
    def default(self) -> Optional[str]:
        return self._default

    @property
    def merge(self) -> bool:
        return self._merge


@dataclasses.dataclass
class CardTemplate:
    name: str
    front: str
    back: str


@dataclasses.dataclass
class Media:
    filename: str
    data: bytes


@dataclasses.dataclass
class Note:
    fields: Dict[str, str] = dataclasses.field(default_factory=dict)
    tags: List[str] = dataclasses.field(default_factory=list)
    media: List[Media] = dataclasses.field(default_factory=list)


class _SourcePluginBase(type):
    def __new__(cls, name, bases, namespaces, **kwargs):
        fields: Dict[str, NoteField] = {}
        field_attributes: Dict[str, str] = {}

        for attribute_name, attribute_value in namespaces.items():
            if isinstance(attribute_value, NoteField):
                attribute_value._set_attribute_name(attribute_name)

                fields[attribute_name] = attribute_value
                field_attributes[attribute_name] = attribute_value

        namespaces.update(field_attributes)
        namespaces["_fields"] = fields

        return super().__new__(cls, name, bases, namespaces, **kwargs)


class SourcePlugin(metaclass=_SourcePluginBase):
    CLOZE = False

    _entrypoint_name: str
    _options: argparse.Namespace
    _console: Console
    _fields: Dict[str, NoteField]

    def __init__(
        self, entrypoint_name: str, options: argparse.Namespace, console: Console
    ):
        self._entrypoint_name = entrypoint_name
        self._options = options
        self._console = console

        super().__init__()

    @property
    def fields(self) -> Dict[str, NoteField]:
        return {v.field_name: v for k, v in self._fields.items()}

    @property
    def console(self) -> Console:
        return self._console

    @property
    def options(self) -> argparse.Namespace:
        return self._options

    def get_model_name(self) -> str:
        return f"Dejima - {self._entrypoint_name}"

    def get_card_templates(self) -> List[CardTemplate]:
        raise NotImplementedError()

    def get_is_cloze(self) -> bool:
        return self.CLOZE

    def get_card_style(self) -> str:
        return ""

    @classmethod
    def get_help(cls) -> Optional[str]:
        return None

    @classmethod
    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        pass

    def get_entries(self) -> Iterable[Tuple[Optional[str], Note]]:
        raise NotImplementedError()

    def resolve_duplicate(self, original: Note, new: Note) -> Note:
        for field_name, field_info in self.fields.items():
            if not field_info.merge:
                continue

            if original.fields.get(field_name) != new.fields.get(field_name):
                original.fields[field_name] = (
                    f"{original.fields[field_name]}\n\n<hr />\n\n"
                    f"{new.fields.get(field_name)}"
                )

        original.tags = list(set(original.tags) | set(new.tags))

        return original


class CommandPlugin(BaseCommand):
    _console: Console

    def __init__(self, options: argparse.Namespace, console: Console):
        self._console: Console = console
        super().__init__(options)

    @property
    def console(self) -> Console:
        return self._console
