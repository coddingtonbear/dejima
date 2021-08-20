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

from .db import Connection as DatabaseConnection
from .api import escape, AnkiError, AnkiNote, Connection as AnkiConnection


def calculate_foreign_key(note: parser.Annotation) -> str:
    data = json.dumps(
        dataclasses.asdict(note),
        sort_keys=True,
        default=str
    )
    return sha256(data.encode('utf-8')).hexdigest()


def main(argv=sys.argv):
    db = DatabaseConnection()
    api = AnkiConnection()

    console = Console()

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        'deck_name',
        type=str,
        choices=api.get_deck_names(),
    )
    arg_parser.add_argument(
        '--model-name',
        default="Basic",
        type=str,
        choices=api.get_model_names(),
    )
    arg_parser.add_argument(
        '--original-text-field',
        default="Front",
        type=str
    )
    arg_parser.add_argument(
        '--annotation-field',
        default="Back",
        type=str
    )
    arg_parser.add_argument(
        '--reimport',
        default=False,
        action='store_true'
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
    merged = 0
    invalid = 0
    total = 0

    annotation_info = parser.get_annotations(args.input)
    for idx, annotation in enumerate(annotation_info.annotations):
        try:
            total += 1
            foreign_key = calculate_foreign_key(annotation)

            if not annotation.original_text:
                console.print(
                    "[yellow]Invalid note (missing 'original_text') "
                    f"[bold]Item {idx}[/bold] "
                    "[/yellow]"
                )
                invalid += 1
                continue
            elif not annotation.annotations:
                console.print(
                    "[yellow]Invalid note (missing 'annotations') "
                    f"[bold]Item {idx}[/bold] "
                    "[/yellow]"
                )
                invalid += 1
                continue

            if args.reimport or not db.annotation_is_known(foreign_key):
                duplicates = api.find_notes(f"""
                    deck:{escape(args.deck_name)}
                    (
                        {args.original_text_field}:{escape(annotation.original_text)}
                        or
                        {args.annotation_field}:{escape(annotation.annotations)}
                    )
                """)
                if duplicates:
                    if len(duplicates) > 1:
                        raise ValueError(
                            f"Multiple duplicate notes found! {duplicates}",
                        )
                    anki_id = duplicates[0]
                    duplicate = api.get_note(anki_id)

                    target_fields = {
                        args.original_text_field: annotation.original_text,
                        args.annotation_field: annotation.annotations,
                    }
                    modified_fields = []
                    for k, v in target_fields.items():
                        if duplicate.fields[k] != v:
                            duplicate.fields[k] = (
                                f"{duplicate.fields[k]}<hr />{v}"
                            )
                            modified_fields.append(k)

                    duplicate.tags.append(import_name)
                    api.update_note(anki_id, duplicate)
                    db.mark_annotation_imported(
                        foreign_key,
                        anki_id,
                        import_name
                    )
                    console.print(
                        "[bright_green]Updated note "
                        f"[bold]{anki_id}[/bold] "
                        f"(fields changed: {','.join(modified_fields)})"
                        "[/bright_green]"
                    )
                    merged += 1
                else:
                    new_note = AnkiNote(
                        args.model_name,
                        {
                            args.original_text_field: annotation.original_text,
                            args.annotation_field: annotation.annotations,
                        },
                        [
                            'boox-import',
                            import_name,
                        ]
                    )
                    anki_id = api.add_note(args.deck_name, new_note)
                    db.mark_annotation_imported(
                        foreign_key,
                        anki_id,
                        import_name
                    )
                    added += 1
                    console.print(
                        "[green]Created note "
                        f"[bold]{anki_id}[/bold]"
                        "[/green]"
                    )
        except Exception:
            console.print_exception(show_locals=True, word_wrap=True)
            console.print(
                f"[red]Added [bold]{added}[/bold] new records[/red] "
                f"({merged} merged; {invalid} invalid; "
                f"{total - added} already processed)"
            )
            console.print(
                f"[red][bold]Import \"{import_name}\" failed.[/bold][/red]"
            )
            sys.exit(1)

    console.print(
        f"[blue]Added [bold]{added}[/bold] new records[/blue] "
        f"({merged} merged; {invalid} invalid; "
        f"{total - added} already processed)"
    )
