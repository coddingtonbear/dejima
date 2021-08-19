"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -mboox_annotations_to_anki` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``boox_annotations_to_anki.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``boox_annotations_to_anki.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
import argparse
import dataclasses
import datetime
from hashlib import sha256
import json
import sys

from rich.console import Console
from boox_annotation_parser import parser

from .api import AnkiError, AnkiNote, AnkiNoteOptions, Connection


def calculate_foreign_key(note: parser.Annotation) -> str:
    data = json.dumps(
        dataclasses.asdict(note),
        sort_keys=True,
        default=str
    )
    return sha256(data.encode('utf-8')).hexdigest()


def main(argv=sys.argv):
    api = Connection()
    console = Console()

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        'deck_name',
        type=str,
        choices=api.get_deck_names(),
    )
    arg_parser.add_argument(
        '-m',
        '--model-name',
        default="Foreign Import",
        type=str,
        choices=api.get_model_names(),
    )
    arg_parser.add_argument(
        '-i',
        '--input',
        nargs='?',
        type=argparse.FileType('r'),
        default=sys.stdin,
        help='File to read from (default: stdin)'
    )
    args = arg_parser.parse_args(argv[1:])

    run_timestamp = datetime.datetime.utcnow()
    import_name = f'import{run_timestamp.strftime("%Y%m%dT%H%M%S")}'

    added = 0
    total = 0

    for annotation in parser.get_annotations(args.input).annotations:
        total += 1
        foreign_key = calculate_foreign_key(annotation)

        if not api.find_notes(
            f'"ForeignKey:{foreign_key}"'
        ):
            new_note = AnkiNote(
                args.deck_name,
                args.model_name,
                {
                    "Front": annotation.original_text,
                    "Back": annotation.annotations,
                    "ForeignKey": foreign_key,
                },
                [import_name]
            )
            try:
                api.add_note(new_note, AnkiNoteOptions(allowDuplicate=True))
                added += 1
            except AnkiError:
                console.print_exception(show_locals=True)
                return
            except Exception:
                console.print_exception(show_locals=True)
                return

    console.print(
        f"[green]Added [bold]{added}[/bold] new records[/green] "
        f"({total - added} duplicates)"
    )
