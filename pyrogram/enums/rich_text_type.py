#  WVLGram - Telegram MTProto API Framework for Python
#  Fork of Pyrogram, modified for private community use.
#  Created by t.me/WannnKW
#
#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

from enum import auto

from .auto_name import AutoName

# Enum tipe rich text. Dipakai saat MEMPARSE teks rich yang diterima.
# Untuk MENGIRIM, hanya sebagian tipe yang didukung server (Layer 227):
#   DIDUKUNG: PLAIN, BOLD, ITALIC, UNDERLINE, STRIKE, CODE, SPOILER, MARKED,
#             SUBSCRIPT, SUPERSCRIPT, URL, EMAIL, PHONE, MATH, ANCHOR, DATE,
#             CONCAT, IMAGE, CUSTOM_EMOJI
#   DITOLAK : MENTION, HASHTAG, CASHTAG, BOT_COMMAND, AUTO_URL, AUTO_EMAIL,
#             AUTO_PHONE, BANK_CARD, MENTION_NAME
# Detailnya ada di pyrogram/types/messages_and_media/rich_text.py


class RichTextType(AutoName):
    """Rich text element type enumeration used in :obj:`~pyrogram.types.RichText`."""

    EMPTY = auto()
    "Empty rich text"

    PLAIN = auto()
    "Plain text"

    BOLD = auto()
    "Bold text"

    ITALIC = auto()
    "Italic text"

    UNDERLINE = auto()
    "Underlined text"

    STRIKE = auto()
    "Strikethrough text"

    CODE = auto()
    "Fixed-width (monospace) text"

    URL = auto()
    "Clickable URL"

    EMAIL = auto()
    "Email address"

    CONCAT = auto()
    "Concatenation of multiple rich text elements"

    SUBSCRIPT = auto()
    "Subscript text"

    SUPERSCRIPT = auto()
    "Superscript text"

    MARKED = auto()
    "Highlighted / marked text"

    PHONE = auto()
    "Phone number"

    IMAGE = auto()
    "Inline image (document)"

    ANCHOR = auto()
    "Named anchor within a document"

    MATH = auto()
    "Mathematical expression (LaTeX source)"

    CUSTOM_EMOJI = auto()
    "Custom emoji"

    SPOILER = auto()
    "Spoiler text"

    MENTION = auto()
    "Auto-detected mention"

    HASHTAG = auto()
    "Auto-detected hashtag"

    BOT_COMMAND = auto()
    "Bot command"

    CASHTAG = auto()
    "Cashtag"

    AUTO_URL = auto()
    "Auto-detected URL"

    AUTO_EMAIL = auto()
    "Auto-detected email"

    AUTO_PHONE = auto()
    "Auto-detected phone number"

    BANK_CARD = auto()
    "Bank card number"

    MENTION_NAME = auto()
    "Explicit mention of a user by ID"

    DATE = auto()
    "Formatted date/time"

    BUTTON = auto()
    "Inline button within rich text"
