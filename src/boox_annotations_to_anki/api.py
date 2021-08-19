import dataclasses
import json
from typing import Any, Dict, List

import requests


@dataclasses.dataclass
class AnkiNoteOptions:
    allowDuplicate: bool = False


@dataclasses.dataclass
class AnkiNote:
    deckName: str
    modelName: str
    fields: Dict[str, str]
    tags: List[str]


class AnkiError(Exception):
    pass


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

    def add_note(self, note, options: AnkiNoteOptions = None) -> int:
        note_data = dataclasses.asdict(note)
        if options is not None:
            note_data["options"] = dataclasses.asdict(options)

        return self._dispatch(
            "addNote",
            {"note": note_data}
        )

    def find_notes(self, query: str) -> List[int]:
        return self._dispatch(
            "findNotes",
            {"query": query},
        )
