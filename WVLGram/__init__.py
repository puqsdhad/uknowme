#  WVLGram - Telegram MTProto API Framework for Python
#  Fork of Pyrogram, modified for private community use.
#  Created by t.me/WannnKW
#
#  WVLGram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  WVLGram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with WVLGram.  If not, see <http://www.gnu.org/licenses/>.

import sys

import pyrogram
from pyrogram import (
    Client,
    ContinuePropagation,
    StopPropagation,
    StopTransmission,
    compose,
    crypto_executor,
    idle,
    __license__,
    __copyright__,
)
from pyrogram import enums, errors, filters, handlers, raw, types

__version__ = pyrogram.__version__


def _install_aliases():
    # WVLGram is a thin alias over the underlying ``pyrogram`` package.
    #
    # Every ``pyrogram.*`` submodule that has already been imported is
    # registered under the matching ``WVLGram.*`` name in ``sys.modules``.
    # This makes ``from WVLGram.xxx import ...`` resolve to the *exact same
    # module objects*, so there are no duplicated classes and ``isinstance``
    # checks keep working.
    for name, module in list(sys.modules.items()):
        if name.startswith("pyrogram."):
            sys.modules.setdefault("WVLGram." + name[len("pyrogram."):], module)


_install_aliases()
del _install_aliases

__all__ = list(pyrogram.__all__)
