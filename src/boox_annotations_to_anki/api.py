import dataclasses
import json
from typing import Any, Dict, List

import requests


@dataclasses.dataclass
class AnkiNoteOptions:
    allowDuplicate: bool = False


@dataclasses.dataclass
class AnkiNote:
    modelName: str
    fields: Dict[str, str]
    tags: List[str]


class AnkiError(Exception):
    pass


class AnkiNoteDoesNotExist(Exception):
    pass


def escape(term: str):
    replacements = {
        '\\': '\\\\',
        '\"': '\\"',
        '*': '\\*',
        '_': '\\_',
        ':': '\\:',
    }
    for fr, to in replacements.items():
        term = term.replace(fr, to)

    return f'"{term}"'


class Connection:
    _hostname: str
    _port: int

    def __init__(self, hostname='127.0.0.1', port=8765):
        self._hostname = hostname
        self._port = port
        self._connection = requests.Session()

        super().__init__()

    def _dispatch(self, action: str, params: Dict[str, Any] = None) -> Any:
        request = self._connection.post(
            f'http://{self._hostname}:{self._port}/',
            data=json.dumps({
                'action': action,
                'version': 6,
                **({"params": params} if params is not None else {})
            })
        )
        request.raise_for_status()

        result = request.json()

        if result["error"] is not None:
            raise AnkiError(result['error'])

        return result["result"]

    def get_deck_names(self) -> List[str]:
        return self._dispatch("deckNames")

    def get_model_names(self) -> List[str]:
        return self._dispatch("modelNames")

    def add_note(self, deck_name: str, note: AnkiNote, options: AnkiNoteOptions = None) -> int:
        note_data = dataclasses.asdict(note)
        if options is not None:
            note_data["options"] = dataclasses.asdict(options)

        note_data["deckName"] = deck_name

        return self._dispatch(
            "addNote",
            {"note": note_data}
        )

    def update_note(self, id: int, note: AnkiNote) -> None:
        note_data = dataclasses.asdict(note)
        note_data['id'] = id

        return self._dispatch(
            "updateNoteFields",
            {"note": note_data}
        )

    def get_note(self, id) -> AnkiNote:
        notes = self._dispatch(
            "notesInfo",
            {"notes": [id]}
        )
        if len(notes) == 0:
            raise AnkiNoteDoesNotExist(id)

        result = notes[0]

        return AnkiNote(
            modelName=result.get('modelName', ''),
            fields={
                k: v['value'] for k, v in result.get('fields', {}).items()
            },
            tags=result.get('tags', [])
        )

    def find_notes(self, query: str) -> List[int]:
        query = query.replace('\n', ' ')
        return self._dispatch(
            "findNotes",
            {"query": query},
        )
