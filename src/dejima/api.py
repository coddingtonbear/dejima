import dataclasses
import json
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import requests


@dataclasses.dataclass
class AnkiMediaUpload:
    filename: str
    data: Optional[str] = None  # Base64'd bytes
    path: Optional[str] = None
    url: Optional[str] = None
    deleteExisting: bool = True


@dataclasses.dataclass
class AnkiCardTemplate:
    Name: str
    Front: str
    Back: str


@dataclasses.dataclass
class AnkiModel:
    modelName: str
    inOrderFields: List[str]
    css: str
    isCloze: bool
    cardTemplates: List[AnkiCardTemplate]


@dataclasses.dataclass
class AnkiNoteOptions:
    allowDuplicate: bool = False


@dataclasses.dataclass
class AnkiNote:
    modelName: str
    deckName: str
    fields: Dict[str, str]
    tags: List[str]


class AnkiError(Exception):
    pass


class AnkiNoteDoesNotExist(Exception):
    pass


def escape(term: str):
    replacements = {
        "\\": "\\\\",
        '"': '\\"',
        "*": "\\*",
        "_": "\\_",
        ":": "\\:",
    }
    for fr, to in replacements.items():
        term = term.replace(fr, to)

    return f'"{term}"'


class Connection:
    _hostname: str
    _port: int

    def __init__(self, hostname="127.0.0.1", port=8765):
        self._hostname = hostname
        self._port = port
        self._connection = requests.Session()

        super().__init__()

    def _dispatch(self, action: str, params: Dict[str, Any] = None) -> Any:
        payload = json.dumps(
            {
                "action": action,
                "version": 6,
                **({"params": params} if params is not None else {}),
            },
            indent=4,
            sort_keys=True,
        )
        request = self._connection.post(
            f"http://{self._hostname}:{self._port}/",
            data=payload,
        )
        request.raise_for_status()

        result = request.json()

        if result["error"] is not None:
            raise AnkiError(result["error"])

        return result["result"]

    def get_deck_names(self) -> List[str]:
        return self._dispatch("deckNames")

    def get_model_names(self) -> List[str]:
        return self._dispatch("modelNames")

    def create_model(self, model: AnkiModel) -> Dict:
        return self._dispatch("createModel", dataclasses.asdict(model))

    def add_note(self, note: AnkiNote, options: AnkiNoteOptions = None) -> int:
        note_data = dataclasses.asdict(note)
        if options is not None:
            note_data.get("options", {}).update(dataclasses.asdict(options))

        return self._dispatch("addNote", {"note": note_data})

    def update_note(self, id: int, note: AnkiNote) -> None:
        note_data = dataclasses.asdict(note)
        note_data["id"] = id

        return self._dispatch("updateNoteFields", {"note": note_data})

    def get_note(self, id) -> AnkiNote:
        notes = self._dispatch("notesInfo", {"notes": [id]})
        if len(notes) == 0:
            raise AnkiNoteDoesNotExist(id)

        result = notes[0]

        return AnkiNote(
            modelName=result.get("modelName", ""),
            deckName=result.get("deckName", ""),
            fields={k: v["value"] for k, v in result.get("fields", {}).items()},
            tags=result.get("tags", []),
        )

    def find_notes(self, query: str) -> List[int]:
        query = query.replace("\n", " ")
        return self._dispatch(
            "findNotes",
            {"query": query},
        )

    def store_media_file(self, media: AnkiMediaUpload) -> str:
        return self._dispatch("storeMediaFile", dataclasses.asdict(media))
