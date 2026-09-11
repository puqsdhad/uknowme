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

from typing import Union, Optional

import pyrogram
from pyrogram import raw, types, utils

from .inline_session import get_session


class SendRichMessageDraft:
    async def send_rich_message_draft(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        rich_message: "types.InputRichMessage",
        message_thread_id: Optional[int] = None,
        reply_to_message_id: Optional[int] = None,
        business_connection_id: Optional[str] = None,
    ) -> bool:
        """Stream a partial rich message as a typing indicator.

        Sends a ``SetTyping`` action with
        ``InputSendMessageRichMessageDraftAction`` so clients display the
        message being composed in real time.  Call repeatedly with updated
        content to stream progressively-generated rich replies.

        Hanya block yang didukung server (lihat
        :obj:`~pyrogram.types.InputRichMessage`) yang bisa dipakai.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Target chat.

            rich_message (:obj:`~pyrogram.types.InputRichMessage`):
                Partial rich message content.

            message_thread_id (``int``, *optional*):
                Forum topic ID.

            reply_to_message_id (``int``, *optional*):
                Message being replied to.

            business_connection_id (``str``, *optional*):
                Unique identifier of the business connection to stream on behalf of.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                from pyrogram.raw import types as raw_types
                from pyrogram.types import InputRichMessage

                # pakai client / c sesuai handler kamu
                await client.send_rich_message_draft(
                    chat_id,
                    InputRichMessage(blocks=[
                        raw_types.PageBlockParagraph(
                            text=raw_types.TextPlain(text="Generating…")
                        )
                    ])
                )
        """
        peer = await self.resolve_peer(chat_id)
        top_msg_id = message_thread_id

        session = None
        if business_connection_id:
            business_connection = self.business_user_connection_cache.get(business_connection_id)
            if business_connection is None:
                business_connection = await self.get_business_connection(business_connection_id)
            session = await get_session(self, business_connection._raw.connection.dc_id)

        rpc = raw.functions.messages.SetTyping(
            peer=peer,
            action=raw.types.InputSendMessageRichMessageDraftAction(
                random_id=self.rnd_id(),
                rich_message=rich_message.write(),
            ),
            top_msg_id=top_msg_id,
        )

        if business_connection_id:
            return await session.invoke(
                raw.functions.InvokeWithBusinessConnection(
                    query=rpc,
                    connection_id=business_connection_id
                )
            )
        return await self.invoke(rpc)
