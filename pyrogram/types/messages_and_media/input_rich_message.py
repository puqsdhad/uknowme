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

from typing import List, Optional

import pyrogram
from pyrogram import raw
from ..object import Object


class InputRichMessage(Object):
    """A rich message to send.

    Pass an instance of this class to :meth:`~pyrogram.Client.send_rich_message` or
    :meth:`~pyrogram.Client.send_rich_message_draft`.

    Parameters:
        blocks (List of ``raw.base.PageBlock``):
            Content blocks. Use raw ``pyrogram.raw.types.PageBlock*`` constructors directly.

        rtl (``bool``, *optional*):
            Pass True for right-to-left content.

        noautolink (``bool``, *optional*):
            Pass True to disable automatic link detection.

    Server support (Layer 227):
        Block yang DIDUKUNG saat mengirim: ``PageBlockParagraph``,
        ``PageBlockPreformatted``, ``PageBlockBlockquote``,
        ``PageBlockBlockquoteBlocks``, ``PageBlockList``,
        ``PageBlockOrderedList``, ``PageBlockTable``, ``PageBlockDetails``,
        ``PageBlockMath``, ``PageBlockAnchor``, ``PageBlockDivider``,
        ``PageBlockFooter``, ``PageBlockButtonRow``, serta
        ``PageBlockPhoto/Video/Audio/Document`` (butuh media valid).

        Block yang TIDAK didukung (ditolak server): ``PageBlockTitle``,
        ``PageBlockSubtitle``, ``PageBlockHeader``, ``PageBlockSubheader``,
        ``PageBlockAuthorDate``, ``PageBlockKicker``, ``PageBlockCover``,
        ``PageBlockThinking``, ``PageBlockCollage``, ``PageBlockSlideshow``.

        Untuk judul/section, pakai ``PageBlockParagraph`` berisi ``TextBold``
        atau ``TextUnderline``.

    Example:
        .. code-block:: python

            from pyrogram.raw import types as raw_types
            from pyrogram.types import InputRichMessage

            # Rich message sederhana (block yang didukung)
            msg = InputRichMessage(blocks=[
                raw_types.PageBlockParagraph(
                    text=raw_types.TextBold(
                        text=raw_types.TextPlain(text="Judul Rich Message")
                    )
                ),
                raw_types.PageBlockDivider(),
                raw_types.PageBlockParagraph(
                    text=raw_types.TextConcat(texts=[
                        raw_types.TextPlain(text="Tebal: "),
                        raw_types.TextBold(text=raw_types.TextPlain(text="bold")),
                        raw_types.TextPlain(text=" miring: "),
                        raw_types.TextItalic(text=raw_types.TextPlain(text="italic")),
                    ])
                ),
                raw_types.PageBlockBlockquote(
                    text=raw_types.TextPlain(text="Ini kutipan panjang..."),
                    caption=raw_types.TextPlain(text="Sumber"),
                ),
                raw_types.PageBlockList(items=[
                    raw_types.PageListItemText(
                        text=raw_types.TextPlain(text="Item selesai"),
                        checkbox=True, checked=True,
                    ),
                    raw_types.PageListItemText(
                        text=raw_types.TextPlain(text="Item biasa"),
                    ),
                ]),
                raw_types.PageBlockPreformatted(
                    text=raw_types.TextPlain(text="print('hi')"),
                    language="python",
                ),
            ])

            # pakai client / c sesuai handler kamu
            await client.send_rich_message(chat_id, msg)

            # Rich message dengan tombol berwarna (banyak tombol)
            msg_with_buttons = InputRichMessage(blocks=[
                raw_types.PageBlockParagraph(
                    text=raw_types.TextPlain(text="Pilih opsi:")
                ),
                raw_types.PageBlockButtonRow(
                    align_center=True,
                    buttons=[
                        raw_types.PageButton(
                            text=raw_types.TextPlain(text="Website"),
                            type=raw_types.InlineButtonTypeUrl(
                                url="https://telegram.org"
                            ),
                            style=raw_types.RichButtonStyle(bg_primary=True),
                        ),
                        raw_types.PageButton(
                            text=raw_types.TextPlain(text="Konfirmasi"),
                            type=raw_types.InlineButtonTypeCallback(data=b"ok"),
                            style=raw_types.RichButtonStyle(bg_success=True),
                        ),
                        raw_types.PageButton(
                            text=raw_types.TextPlain(text="Batalkan"),
                            type=raw_types.InlineButtonTypeCallback(data=b"no"),
                            style=raw_types.RichButtonStyle(bg_danger=True),
                        ),
                    ],
                ),
            ])
            await client.send_rich_message(chat_id, msg_with_buttons)
    """

    def __init__(
        self,
        *,
        blocks: List["raw.base.PageBlock"],
        rtl: bool = False,
        noautolink: bool = False,
    ):
        super().__init__(None)
        self.blocks = blocks
        self.rtl = rtl
        self.noautolink = noautolink

    def write(self) -> "raw.types.InputRichMessage":
        return raw.types.InputRichMessage(
            blocks=self.blocks,
            rtl=self.rtl or None,
            noautolink=self.noautolink or None,
        )
