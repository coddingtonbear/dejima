import argparse
import base64
import dataclasses
import mimetypes
import sys
import uuid
from hashlib import sha256
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from lln_json_parser import parser
from lln_json_parser import types

from ..plugin import CardTemplate
from ..plugin import Media
from ..plugin import Note
from ..plugin import NoteField
from ..plugin import SourcePlugin


@dataclasses.dataclass
class MediaDescriptor:
    filename: str
    field_value: str
    file_data: bytes


class LLNJsonSource(SourcePlugin):
    Source = NoteField()
    SourceLanguage = NoteField(optional=True)

    HumanTranslation = NoteField()
    MachineTranslation = NoteField(optional=True)
    TranslationLanguage = NoteField(optional=True)

    ThumbnailPre = NoteField(optional=True)
    ThumbnailPost = NoteField(optional=True)
    Audio = NoteField(optional=True)

    Reverse = NoteField(field_name="Add Reverse", optional=True)

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
                name="Source to Translation",
                front="""
                    <p>
                        {{ThumbnailPre}}
                    </p>
                    <p>
                        {{Source}}
                    </p>
                    <p>
                        {{ThumbnailPost}}
                    </p>
                    <div style="display: none;">{{Audio}}</div>
                """,
                back="""
                    <p>
                        {{FrontSide}}
                    </p>
                    <hr id='answer' />
                    <p>
                        {{HumanTranslation}}<br />
                        {{#MachineTranslation}}
                            <i>({{MachineTranslation}})</i>
                        {{/MachineTranslation}}
                    </p>
                """,
            ),
            CardTemplate(
                name="Translation to Source",
                front="""
                    {{#Add Reverse}}
                        <p>
                            {{HumanTranslation}}
                        </p>
                    {{/Add Reverse}}
                """,
                back="""
                    {{FrontSide}}
                    <hr id='answer' />
                    <p>
                        {{ThumbnailPre}}
                    </p>
                    <p>
                        {{Source}}
                    </p>
                    <p>
                        {{ThumbnailPost}}
                    </p>
                    <div style="display: none;">{{Audio}}</div>
                """,
            ),
        ]

    def _calculate_key(self, saved: Union[types.SavedPhrase, types.SavedWord]) -> str:
        data = saved.json(sort_keys=True)
        return sha256(data.encode("utf-8")).hexdigest()

    @classmethod
    def add_arguments(self, arg_parser: argparse.ArgumentParser) -> None:
        arg_parser.add_argument(
            "-i",
            "--input",
            nargs="?",
            type=argparse.FileType("r"),
            default=sys.stdin,
            help="File to read from (default: stdin)",
        )
        return super().add_arguments(arg_parser)

    def _generate_media_data(
        self, media: Union[types.Thumbnail, types.Audio]
    ) -> Optional[Tuple[str, bytes]]:
        if not media or not media.data_url:
            return None

        mime_type, _ = mimetypes.guess_type(media.data_url)
        if not mime_type:
            return None

        extension = mimetypes.guess_extension(mime_type)
        if not extension:
            return None

        filename = f"{uuid.uuid4()}{extension}"
        _, encoded_data = media.data_url.split(",")

        return filename, base64.b64decode(encoded_data)

    def _get_thumbnail_media_descriptor(
        self, thumbnail: Optional[types.Thumbnail]
    ) -> Optional[MediaDescriptor]:
        media_data = self._generate_media_data(thumbnail)
        if not media_data:
            return None

        filename, data = media_data

        return MediaDescriptor(filename, f"<img src='{filename}' />", data)

    def _get_audio_media_descriptor(
        self, audio: Optional[types.Audio]
    ) -> Optional[MediaDescriptor]:
        media_data = self._generate_media_data(audio)
        if not media_data:
            return None

        filename, data = media_data

        return MediaDescriptor(filename, f"[sound:{filename}]", data)

    def _get_media_for_phrase(
        self, phrase: types.Phrase
    ) -> Tuple[List[Media], Dict[str, str]]:
        media: List[Media] = []
        fields: Dict[str, str] = {}

        thumb_prev: Optional[MediaDescriptor] = self._get_thumbnail_media_descriptor(
            phrase.thumb_prev
        )
        if thumb_prev:
            fields[self.ThumbnailPre.field_name] = thumb_prev.field_value
            media.append(Media(thumb_prev.filename, thumb_prev.file_data))

        thumb_next: Optional[MediaDescriptor] = self._get_thumbnail_media_descriptor(
            phrase.thumb_next
        )
        if thumb_next:
            fields[self.ThumbnailPost.field_name] = thumb_next.field_value
            media.append(Media(thumb_next.filename, thumb_next.file_data))

        audio: Optional[MediaDescriptor] = self._get_audio_media_descriptor(
            phrase.audio
        )
        if audio:
            fields[self.Audio.field_name] = audio.field_value
            media.append(Media(audio.filename, audio.file_data))

        return media, fields

    def _get_note_for_saved_word(self, saved: types.SavedWord) -> Note:
        fields: Dict[str, str] = {
            self.Source.field_name: (
                f'{saved.word.text}<br /><i>"{saved.context.phrase.subtitles.target}"</i>'
            ),
            self.SourceLanguage.field_name: saved.lang_code,
            self.HumanTranslation.field_name: (
                f"{', '.join(saved.word_translations)}<br />"
                f'<i>"{saved.context.phrase.human_translations.target}"</i>'
            ),
            self.MachineTranslation.field_name: (
                saved.context.phrase.machine_translations.target
            ),
            self.TranslationLanguage.field_name: saved.translation_lang_code,
        }

        media, extra_fields = self._get_media_for_phrase(saved.context.phrase)
        fields.update(extra_fields)

        return Note(fields=fields, media=media)

    def _get_note_for_saved_phrase(self, saved: types.SavedPhrase) -> Note:
        fields: Dict[str, str] = {
            self.Source.field_name: saved.context.phrase.subtitles.target,
            self.SourceLanguage.field_name: saved.lang_code,
            self.HumanTranslation.field_name: saved.context.phrase.human_translations.target,
            self.MachineTranslation.field_name: (
                saved.context.phrase.machine_translations.target
            ),
            self.TranslationLanguage.field_name: saved.translation_lang_code,
        }

        media, extra_fields = self._get_media_for_phrase(saved.context.phrase)
        fields.update(extra_fields)

        return Note(fields=fields, media=media)

    def get_entries(self) -> Iterable[Tuple[str, Note]]:
        entries = parser.get_entries(self.options.input)

        for entry in entries:
            foreign_key = self._calculate_key(entry)

            if isinstance(entry, types.SavedPhrase):
                note = self._get_note_for_saved_phrase(entry)
            elif isinstance(entry, types.SavedWord):
                note = self._get_note_for_saved_word(entry)
            else:
                raise ValueError(f"Unexpected note type: {entry}")

            yield foreign_key, note
