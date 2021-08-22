import argparse
import dataclasses
import json
import sys
from hashlib import sha256
from typing import Iterable
from typing import List
from typing import Tuple

from boox_annotation_parser import parser as boox_parser

from ..plugin import CardTemplate
from ..plugin import Note
from ..plugin import NoteField
from ..plugin import SourcePlugin


class BooxSource(SourcePlugin):
    Front = NoteField(unique=True, merge=True)
    Back = NoteField(unique=True, merge=True)
    Reverse = NoteField(default="1", field_name="Add Reverse", optional=True)

    def get_card_style(self) -> str:
        return """
            .card {
                font-family: arial;
                font-size: 20px;
                text-align: center;
                color: black;
                background-color: white;
            }
        """

    def get_card_templates(self) -> List[CardTemplate]:
        return [
            CardTemplate(
                name="Card 1",
                front="<p>{{Front}}</p>",
                back="""
                    {{FrontSide}}
                    <hr id='answer' />
                    <p>
                        {{Back}}
                    </p>
                """,
            ),
            CardTemplate(
                name="Card 2",
                front="""
                    {{#Add Reverse}}
                        <p>
                            {{Back}}
                        </p>
                    {{/Add Reverse}}
                """,
                back="""
                    {{FrontSide}}
                    <hr id='answer' />
                    <p>
                        {{Front}}
                    </p>
                """,
            ),
        ]

    @classmethod
    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "-i",
            "--input",
            nargs="?",
            type=argparse.FileType("r"),
            default=sys.stdin,
            help="File to read from (default: stdin)",
        )
        return super().add_arguments(parser)

    def _calculate_key(self, note: boox_parser.Annotation) -> str:
        data = json.dumps(dataclasses.asdict(note), sort_keys=True, default=str)
        return sha256(data.encode("utf-8")).hexdigest()

    def get_entries(self) -> Iterable[Tuple[str, Note]]:
        annotation_info = boox_parser.get_annotations(self.options.input)
        for annotation in annotation_info.annotations:
            foreign_key = self._calculate_key(annotation)
            note = Note(
                fields={
                    self.Front.field_name: annotation.original_text,
                    self.Back.field_name: annotation.annotations,
                }
            )
            yield foreign_key, note
