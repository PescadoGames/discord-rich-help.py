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

import asyncio
from typing import Optional, TYPE_CHECKING

from discord import Color, Embed
from discord.app_commands import command, describe, locale_str, rename
from discord.ext.commands import Cog, Context, Group, HelpCommand

from .text import text

if TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Any, List, Tuple, Union

    from discord import Interaction, Locale
    from discord.abc import MessageableChannel
    from discord.ext.commands import BotBase, Command

__all__ = (
    'RichHelpCommand',
)


class RichHelpCommand(HelpCommand, Cog):
    """
    The class for a rich help command.

    .. versionadded:: 0.1
    """

    __slots__ = (
        '_last_member',
        'embed_color',
    )

    def __init__(self, *, color: Union[Color, int] = Color.blurple()) -> None:
        """

        .. versionadded:: 0.1
        """
        super().__init__(command_attrs={'help': 'Show this message'})
        self._last_member = None
        self.embed_color: Union[Color, int] = color

    def _add_to_bot(self, bot: BotBase) -> None:
        super()._add_to_bot(bot)
        asyncio.run(bot.add_cog(self))

    def _remove_from_bot(self, bot: BotBase) -> None:
        super()._remove_from_bot(bot)
        asyncio.run(bot.remove_cog(__class__.__name__))

    def is_interaction_based(self) -> bool:
        """

        .. versionadded:: 0.1
        """
        if self.context.interaction is not None:
            return True

        else:
            return False

    async def send_bot_help(self, mapping: Mapping[Optional[Cog], List[Command]]) -> None:
        """|coro|

        .. versionadded:: 0.1
        """
        prefix: Optional[str] = self.context.prefix
        bot_help: Embed = Embed(title='Command help', color=self.embed_color)
        filtered: List[Command[Any, Any, Any]]

        if self.is_interaction_based():
            filtered = await self.filter_commands(self.context.bot.tree.get_commands(), sort=True)
            for command in filtered:
                params = [f'[{p.display_name}]' for p in command.parameters]
                param_str = ' '.join(params) if params else ''
                bot_help.add_field(
                    name=f'{prefix}{command.name} {param_str}',
                    value=command.description,
                    inline=False
                )

        else:
            filtered = await self.filter_commands(self.context.bot.commands, sort=True)
            for command in filtered:
                bot_help.add_field(
                    name=f'{prefix}{command.name} {command.signature}',
                    value=command.short_doc,
                    inline=False
                )

        await self.get_destination().send(embed=bot_help)

    async def send_cog_help(self, cog: Cog) -> None:
        """|coro|

        .. versionadded:: 0.1
        """
        await self.send_error_message(self.command_not_found(cog.qualified_name))

    async def send_group_help(self, group: Group) -> None:
        """|coro|

        .. versionadded:: 0.1
        """
        prefix: Optional[str] = self.context.prefix
        group_help: Embed = Embed(
            title=f"{prefix}{group.qualified_name} {group.signature}",
            description=group.help,
            color=self.embed_color
        )
        filtered: List[Command[Any, Any, Any]] = await self.filter_commands(group.commands, sort=True)
        for child in filtered:
            group_help.add_field(
                name=f"{prefix}{child.qualified_name} {group.signature}",
                value=child.short_doc,
                inline=False
            )

        await self.get_destination().send(embed=group_help)

    async def send_command_help(self, command: Command) -> None:
        """|coro|

        .. versionadded:: 0.1
        """
        prefix: Optional[str] = self.context.prefix
        cmd_help: Embed = Embed(
            title=f"{prefix}{command.qualified_name} {command.signature}",
            description=command.help,
            color=self.embed_color
        )
        if isinstance(command, Group):
            filtered: List[Command[Any, Any, Any]] = await self.filter_commands(command.commands, sort=True)
            for child in filtered:
                cmd_help.add_field(
                    name=f"{prefix}{child.qualified_name} {child.signature}",
                    value=child.short_doc,
                    inline=False
                )

        await self.get_destination().send(embed=cmd_help)

    async def filter_commands(
            self,
            commands: List[Command[Any, Any, Any]],
            *,
            sort: Optional[bool] = False
    ) -> List[Command[Any, Any, Any]]:
        """

        .. versionadded:: 0.1
        """
        try:
            return await super().filter_commands(commands, sort=sort)

        except Exception:
            if sort:
                dic = dict(zip([cmd.name for cmd in commands], commands))
                return [i[1] for i in sorted(dic.items())]

            else:
                return commands

    def get_destination(self) -> Context[Any]:
        """

        .. versionadded:: 0.1
        """
        return self.context

    def command_not_found(self, string: str) -> str:
        """|maybecoro|

        .. versionadded:: 0.1
        """
        return super().command_not_found(string)

    def subcommand_not_found(self, command: Command[Any, Any, Any], string: str) -> str:
        """|maybecoro|

        .. versionadded:: 0.1
        """
        return super().subcommand_not_found(command, string)

    async def send_error_message(self, error: str) -> None:
        """|coro|

        .. versionadded:: 0.1
        """
        err: Embed = Embed(title=error, color=Color.red())
        await self.get_destination().send(embed=err)

    @command(name='help', description=locale_str(text['default_help_doc']))
    @describe(
        cmd=locale_str(text['cmd_doc']),
        subcmd=locale_str(text['subcmd_doc'])
    )
    @rename(cmd=locale_str(text['cmd']), subcmd=locale_str(text['subcmd']))
    async def slash_help(self, interaction: Interaction, cmd: Optional[str] = None, subcmd: Optional[str] = None) -> None:
        self.context = await Context.from_interaction(interaction)
        param: Optional[str]

        if cmd is not None and subcmd is None:
            param = cmd

        elif cmd is not None and subcmd is not None:
            param = f'{cmd} {subcmd}'

        else:
            param = None

        await self.context.bot.help_command.command_callback(self.context, command=param)
