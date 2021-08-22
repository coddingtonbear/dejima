import argparse
import base64
import datetime
from textwrap import dedent
from typing import List

from ..api import AnkiCardTemplate
from ..api import AnkiMediaUpload
from ..api import AnkiModel
from ..api import AnkiNote
from ..api import AnkiNoteOptions
from ..api import Connection as AnkiConnection
from ..api import escape
from ..db import Connection as DatabaseConnection
from ..plugin import CommandPlugin
from ..plugin import Note
from ..plugin import get_installed_sources


class ImportCommand(CommandPlugin):
    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        sources = get_installed_sources()

        parser.add_argument("deck_name", type=str)
        parser.add_argument("--reimport", action="store_true", default=False)
        subparsers = parser.add_subparsers(dest="source")
        subparsers.required = True

        for src_name, src_class in sources.items():
            parser_kwargs = {}

            src_help = src_class.get_help()
            if src_help:
                parser_kwargs["help"] = src_help

            subparser = subparsers.add_parser(src_name, **parser_kwargs)
            src_class.add_arguments(subparser)

        return super().add_arguments(parser)

    def handle(self) -> None:
        run_timestamp = datetime.datetime.utcnow()
        import_name = f'import{run_timestamp.strftime("%Y%m%dT%H%M%S")}'

        db = DatabaseConnection()
        api = AnkiConnection()

        sources = get_installed_sources()
        source = sources[self.options.source](
            self.options.source,
            self.options,
            self.console,
        )

        model_name = source.get_model_name()
        if model_name not in api.get_model_names():
            model = AnkiModel(
                source.get_model_name(),
                list(source.fields.keys()),
                source.get_card_style(),
                source.get_is_cloze(),
                [
                    AnkiCardTemplate(
                        Name=dedent(t.name).strip(),
                        Front=dedent(t.front).strip(),
                        Back=dedent(t.back).strip(),
                    )
                    for t in source.get_card_templates()
                ],
            )
            api.create_model(model)

        added = 0
        merged = 0
        invalid = 0
        total = 0

        for idx, (foreign_key, entry) in enumerate(source.get_entries()):
            try:
                total += 1
                if (
                    not foreign_key
                    or self.options.reimport
                    or not db.annotation_is_known(self.options.source, foreign_key)
                ):
                    note_is_valid = True
                    for field_name, field_info in source.fields.items():
                        if not field_info.optional and not entry.fields.get(field_name):
                            self.console.print(
                                f"[yellow]Invalid note (missing '{field_name}') "
                                f"[bold]Idx {idx}[/bold] "
                                "[/yellow]"
                            )
                            invalid += 1
                            note_is_valid = False
                            if foreign_key:
                                db.mark_entry_processed(
                                    self.options.source, foreign_key, None, import_name
                                )

                        if field_info.default and field_name not in entry.fields:
                            entry.fields[field_name] = field_info.default
                    if not note_is_valid:
                        continue
                    clauses: List[str] = []
                    for field_name, field_info in source.fields.items():
                        if field_info.unique:
                            clauses.append(
                                f"{field_name}:{escape(entry.fields.get(field_name, ''))}"
                            )
                            pass

                    duplicates = []
                    if clauses:
                        duplicates = api.find_notes(
                            f"""
                            deck:{escape(self.options.deck_name)}
                            (
                                {' or '.join(clauses)}
                            )
                        """
                        )

                    if duplicates:
                        if len(duplicates) > 1:
                            self.console.print(
                                "[red]Multiple duplicate notes found for "
                                f"entry {entry} (idx: {idx}): "
                                f"{duplicates}.[/red]"
                            )

                        anki_id = duplicates[0]
                        duplicate_anki = api.get_note(anki_id)

                        duplicate_note = Note(
                            fields=duplicate_anki.fields, tags=duplicate_anki.tags
                        )

                        anki_note = source.resolve_duplicate(duplicate_note, entry)

                        duplicate_anki.fields = anki_note.fields
                        duplicate_anki.tags = anki_note.tags

                        api.update_note(anki_id, duplicate_anki)
                        if foreign_key:
                            db.mark_entry_processed(
                                self.options.source, foreign_key, anki_id, import_name
                            )
                        self.console.print(
                            "[bright_green]Updated note "
                            f"[bold]{anki_id}[/bold][/bright_green]"
                        )
                        merged += 1
                    else:
                        new_note = AnkiNote(
                            model_name,
                            self.options.deck_name,
                            entry.fields,
                            entry.tags
                            + [
                                "dejima-import",
                                import_name,
                            ],
                        )
                        anki_id = api.add_note(
                            new_note, AnkiNoteOptions(allowDuplicate=True)
                        )
                        if foreign_key:
                            db.mark_entry_processed(
                                self.options.source, foreign_key, anki_id, import_name
                            )
                        added += 1
                        self.console.print(
                            "[green]Created note " f"[bold]{anki_id}[/bold]" "[/green]"
                        )

                    # We can upload the media regardless of whether
                    # this element turns out to be a duplicate --
                    # Anki will search for and find unreferenced media
                    # automatically.
                    for media in entry.media:
                        api.store_media_file(
                            AnkiMediaUpload(
                                filename=media.filename,
                                data=base64.b64encode(media.data).decode("ascii"),
                            )
                        )

            except Exception:
                self.console.print(
                    f"[red]Added [bold]{added}[/bold] new records[/red] "
                    f"({merged} merged; {invalid} invalid; "
                    f"{total - added - invalid - merged} already processed)"
                )
                self.console.print(
                    f'[red][bold]Import "{import_name}" failed.[/bold][/red]'
                )
                raise

        self.console.print(
            f"[blue]Added [bold]{added}[/bold] new records[/blue] "
            f"({merged} merged; {invalid} invalid; "
            f"{total - added - invalid - merged} already processed)"
        )
