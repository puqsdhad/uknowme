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

from typing import Union

import pyrogram
from pyrogram import raw
from pyrogram import types


class JoinChat:
    async def join_chat(
        self: "pyrogram.Client",
        chat_id: Union[int, str]
    ) -> "types.Chat":
        """Join a group chat or channel.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier for the target chat in form of a *t.me/joinchat/* link, a username of the target
                channel/supergroup (in the format @username) or a chat id of a linked chat (channel or supergroup).

        Returns:
            :obj:`~pyrogram.types.Chat`: On success, a chat object is returned.

        Example:
            .. code-block:: python

                # Join chat via invite link
                await app.join_chat("https://t.me/+AbCdEf0123456789")

                # Join chat via username
                await app.join_chat("pyrogram")

                # Join a linked chat
                await app.join_chat(app.get_chat("pyrogram").linked_chat.id)
        """
        match = self.INVITE_LINK_RE.match(str(chat_id))

        if match:
            result = await self.invoke(
                raw.functions.messages.ImportChatInvite(
                    hash=match.group(1)
                )
            )
        else:
            result = await self.invoke(
                raw.functions.channels.JoinChannel(
                    channel=await self.resolve_peer(chat_id)
                )
            )

        chats = getattr(result, "chats", None)

        if chats is None:
            updates = getattr(result, "updates", None)

            if updates is None:
                raise ValueError(
                    "Join chat: response tidak memuat data chat, mungkin butuh webview"
                )

            chats = getattr(updates, "chats", None) or []
            await self.fetch_peers(chats)
            await self.fetch_peers(getattr(updates, "users", None) or [])

        for chat in chats:
            if isinstance(chat, raw.types.Chat):
                return types.Chat._parse_chat_chat(self, chat)

            if isinstance(chat, raw.types.Channel):
                return types.Chat._parse_channel_chat(self, chat)

        return await self.get_chat(chat_id)
