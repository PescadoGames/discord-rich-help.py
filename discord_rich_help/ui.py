"""
MIT License

Copyright (c) 2023 PescadoGames

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from discord import ButtonStyle, Message
from discord.ui import View, button

if TYPE_CHECKING:
    from typing import Any, Awaitable, Callable, Dict, TypeAlias

    from discord import Interaction, Message
    from discord.ui import Button

    ItemId: TypeAlias = Literal['category', 'command', 'first', 'back', 'next', 'last']
    F: TypeAlias = Callable[[ItemId, Interaction, Button, HelpCommandView], Awaitable[Any]]
    HelpType: TypeAlias = Literal['bot', 'category', 'command', 'group']

__all__ = (
    'HelpCommandView',
)


class HelpCommandView(View):
    """

    .. versionadded:: 0.1
    """
    __slots__ = (
        '__button_callback',
        'message',
    )

    def __init__(
            self,
            *,
            page_length: int,
            button_callback: F,
    ) -> None:
        """

        .. versionadded:: 0.1
        """
        super().__init__()
        self.message: Optional[Message] = None
        self.__button_callback: F = button_callback

        if page_length == 1:
            setattr(self.next_button, 'disabled', True)
            setattr(self.last_button, 'disabled', True)

    @button(style=ButtonStyle.secondary, label='≪', disabled=True)
    async def first_button(self, interaction: Interaction, button: Button) -> None:
        """

        .. versionadded:: 0.1
        """
        await self.__button_callback('first', interaction, button, self)

    @button(style=ButtonStyle.primary, label='Back', disabled=True)
    async def back_button(self, interaction: Interaction, button: Button) -> None:
        """

        .. versionadded:: 0.1
        """
        await self.__button_callback('back', interaction, button, self)

    @button(style=ButtonStyle.primary, label='Next')
    async def next_button(self, interaction: Interaction, button: Button) -> None:
        """

        .. versionadded:: 0.1
        """
        await self.__button_callback('next', interaction, button, self)

    @button(style=ButtonStyle.secondary, label='≫')
    async def last_button(self, interaction: Interaction, button: Button) -> None:
        """

        .. versionadded:: 0.1
        """
        await self.__button_callback('last', interaction, button, self)

    async def on_timeout(self) -> None:
        """

        .. versionadded:: 0.1
        """
        if self.message is None:
            raise ValueError('"message" is not defined')

        for item in self.children:
            setattr(item, 'disabled', True)
        self.timeout = 0

        await self.message.edit(view=self)
