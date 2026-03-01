from discord import Embed, File
import os
import pathlib

from .EntryLabels import TITLE_LABEL, DESCRIPTION_LABEL, IMAGE_LABEL, FIELD_LIST_LABEL, \
    FIELD_HEADER_LABEL, FIELD_TEXT_LABEL, FIELD_INLINE_LABEL, FIELD_SUBLIST_LABEL, \
    FORMAT_TITLE_LABEL, FORMAT_FIELD_HEADER_LABEL, FORMAT_FIELD_TEXT_LABEL, FORMAT_DESCRIPTION_LABEL


def get_format_or_default(format_info, format_label, value_label) -> str:
    return format_info[format_label] if format_label in format_info else f'{{{value_label}}}'


def get_class_image_filepath(classname: str) -> str:
    this_file_folder_path = pathlib.Path(__file__).parent.resolve()
    return os.path.join(this_file_folder_path, os.sep.join(['Assets', 'classes', f'{classname}.png']))


class WikiEntry:
    def __init__(self, entry_info, format_info):
        self.title_format = get_format_or_default(format_info, FORMAT_TITLE_LABEL, TITLE_LABEL)
        self.description_format = get_format_or_default(format_info, FORMAT_DESCRIPTION_LABEL, DESCRIPTION_LABEL)
        self.field_header_format = get_format_or_default(format_info, FORMAT_FIELD_HEADER_LABEL, FIELD_HEADER_LABEL)
        self.field_text_format = get_format_or_default(format_info, FORMAT_FIELD_TEXT_LABEL, FIELD_TEXT_LABEL)
        self.entry_info = entry_info
        self.title = entry_info[TITLE_LABEL]
        self.image = bool(entry_info[IMAGE_LABEL]) if IMAGE_LABEL in entry_info else False
        self.fields = entry_info[FIELD_LIST_LABEL] if FIELD_LIST_LABEL in entry_info else []
        if DESCRIPTION_LABEL not in entry_info:
            entry_info[DESCRIPTION_LABEL] = ""

    def get_entry_embed(self) -> tuple[Embed, File]:
        embed = Embed(title=self.title_format.format(**self.entry_info), description=self.description_format.format(**self.entry_info))
        file = None
        if self.image:
            file = File(get_class_image_filepath(self.title.lower()))
            embed.set_image(url=f'attachment://{file.filename}')

        for field in self.fields:
            field_inline = bool(field[FIELD_INLINE_LABEL]) if FIELD_INLINE_LABEL in field else True
            if FIELD_SUBLIST_LABEL in field:
                field[FIELD_TEXT_LABEL] = "".join([f'> {value}\n' for value in field[FIELD_SUBLIST_LABEL]])
            embed.add_field(
                inline=field_inline,
                name=self.field_header_format.format(**field),
                value=self.field_text_format.format(**field)
            )
        return embed, file

    def add_field(self, header="", text="", inline=True):
        self.fields.append({
            FIELD_HEADER_LABEL: header,
            FIELD_TEXT_LABEL: text,
            FIELD_INLINE_LABEL: inline
        })
