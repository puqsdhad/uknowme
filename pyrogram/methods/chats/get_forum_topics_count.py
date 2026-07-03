#  Pyrofork - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#  Copyright (C) 2022-present Mayuri-Chan <https://github.com/Mayuri-Chan>
#
#  This file is part of Pyrofork.
#
#  Pyrofork is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrofork is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrofork.  If not, see <http://www.gnu.org/licenses/>.

import pyrogram
from pyrogram import raw
from typing import Union

class GetForumTopicsCount:
    async def get_forum_topics_count(
        self: "pyrogram.Client",
        chat_id: Union[int, str]
    ) -> int:
        r = await self.invoke(
            raw.functions.messages.GetForumTopics(
                peer=await self.resolve_peer(chat_id),
                offset_date=0,
                offset_id=0,
                offset_topic=0,
                limit=0
            )
        )
        return getattr(r, "count", 0)
