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

from typing import Callable

from .handler import Handler


class BusinessMessageHandler(Handler):
    """The BusinessMessage handler class. Used to handle new messages from a connected business account.
    It is intended to be used with :meth:`~pyrogram.Client.add_handler`

    For a nicer way to register this handler, have a look at the
    :meth:`~pyrogram.Client.on_business_message` decorator.

    Parameters:
        callback (``Callable``):
            Pass a function that will be called when a new business Message arrives. It takes *(client, message)*
            as positional arguments.

        filters (:obj:`Filters`):
            Pass one or more filters to allow only a subset of messages to be passed
            in your callback function.

    Other parameters:
        client (:obj:`~pyrogram.Client`):
            The Client itself, useful when you want to call other API methods inside the handler.

        message (:obj:`~pyrogram.types.Message`):
            The received message. The business connection identifier is available as
            ``message.business_connection_id``.
    """

    def __init__(self, callback: Callable, filters=None):
        super().__init__(callback, filters)
