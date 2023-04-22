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
from discord.app_commands import command as slash_command
from discord.app_commands import describe, locale_str, rename
from discord.ext.commands import Cog, Context, Group, HelpCommand

from .text import text
from .ui import HelpCommandView

if TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Any, Generator, Iterable, List, Union
    from typing_extensions import TypeAlias

    from discord import Interaction
    from discord.app_commands import Command as SlashCommand
    from discord.ui import Button, View
    from discord.ext.commands import Command
    from discord.ext.commands.bot import BotBase

    from .ui import ItemId

    AnyCommand: TypeAlias = Union[Command[Any, ..., Any], SlashCommand[Any, ..., Any]]

__all__ = (
    'RichHelpCommand',
)


class RichHelpCommand(HelpCommand, Cog):
    """A class for a rich help command.

    .. versionadded:: 0.1

    Parameters
    -----------
    embed_color: Union[:class:`Color`, :class:`int`]
        An embed color for help commands.

    Attributes
    -----------
    embed_color: Union[:class:`Color`, :class:`int`]
        An embed color for help commands.
    """

    __slots__ = (
        '_last_member',
        'embed_color',
        'current_page',
        'pages',
    )

    def __init__(self, *, embed_color: Union[Color, int] = Color.blurple()) -> None:
        super().__init__(command_attrs={'help': 'Show this message'})
        self._last_member = None
        self.current_page: int
        self.pages: List[List[AnyCommand]]
        self.embed_color: Union[Color, int] = embed_color

    def _add_to_bot(self, bot: BotBase) -> None:
        """Add help commands to `bot` .

        .. versionadded:: 0.1
        """
        super()._add_to_bot(bot)
        asyncio.run(bot.add_cog(self))

    def _remove_from_bot(self, bot: BotBase) -> None:
        """Remove help commands from `bot` .

        .. versionadded:: 0.1
        """
        super()._remove_from_bot(bot)
        asyncio.run(bot.remove_cog(__class__.__name__))  # type: ignore

    def is_interaction_based(self) -> bool:
        """Check if a command is a message command or a slash command.

        .. versionadded:: 0.1

        Returns
        --------
        :class:`bool`
            Return True if a command is slash command.
        """
        if self.context.interaction is not None:
            return True

        else:
            return False

    def _split_list(self, base: List[Any], length: int) -> Generator[List[Any], None, None]:
        """Split a list.

        .. versionadded:: 0.1

        Parameters
        -----------
        base: List[Any]
            A list to split.
        length: :class:`int`
            A max length of each list.

        Yields
        -------
        List[Any]
            A split list.
        """
        for idx in range(0, len(base), length):
            yield base[idx:idx + length]

    def get_pages(self, commands: List[AnyCommand]) -> List[List[AnyCommand]]:
        """Split a list of commands to display.

        .. versionadded:: 0.1

        Parameters
        -----------
        commands: List[:class:`AnyCommand`]
            A list of commands

        Returns
        --------
        List[List[:class:`AnyCommand`]]
        """
        return list(self._split_list(commands, 10))

    async def switch_page(self, id: ItemId, interaction: Interaction, button: Button[View], view: HelpCommandView) -> None:
        """Switch a page of help command embed.

        This function must be given as an argument of :class:`HelpCommandView` .

        .. versionadded:: 0.1

        Parameters
        -----------
        id: :class:`ItemId`
            A type of button or select menu.
        interaction: :class:`Interaction`
        view: :class:`HelpCommandView`
        """
        page_length: int = len(self.pages)

        if id == 'first':
            self.current_page = 1

        elif id == 'back':
            self.current_page = self.current_page - 1

        elif id == 'next':
            self.current_page = self.current_page + 1

        elif id == 'last':
            self.current_page = page_length

        if self.current_page == page_length:
            setattr(view.first_button, 'disabled', False)
            setattr(view.back_button, 'disabled', False)
            setattr(view.next_button, 'disabled', True)
            setattr(view.last_button, 'disabled', True)

        elif self.current_page == 1:
            setattr(view.first_button, 'disabled', True)
            setattr(view.back_button, 'disabled', True)
            if not page_length == 1:
                setattr(view.next_button, 'disabled', False)
                setattr(view.last_button, 'disabled', False)

        new_page: Embed = self.get_bot_help()
        await interaction.response.edit_message(embed=new_page, view=view)

    def get_bot_help(self) -> Embed:
        """Make an embed of bot help command.

        .. versionadded:: 0.1

        Returns
        --------
        :class:`Embed`
            An embed of bot help command.
        """
        prefix: Optional[str] = self.context.prefix
        page_length: int = len(self.pages)
        bot_help: Embed = Embed(title=text['help_title'], color=self.embed_color)
        bot_help.set_footer(text=f'Page {self.current_page}/{page_length}')

        if self.is_interaction_based():
            for command in self.pages[self.current_page - 1]:
                params = [f'[{p.display_name}]' for p in command.parameters]  # type: ignore
                param_str = ' '.join(params) if params else ''
                bot_help.add_field(
                    name=f'{prefix}{command.name} {param_str}',
                    value=command.description,
                    inline=False
                )

        else:
            for command in self.pages[self.current_page - 1]:
                bot_help.add_field(
                    name=f'{prefix}{command.name} {command.signature}',  # type: ignore
                    value=command.short_doc,  # type: ignore
                    inline=False
                )

        return bot_help

    async def send_bot_help(self, mapping: Mapping[Optional[Cog], List[Command[Any, Any, Any]]]) -> None:
        """|coro|

        Send a bot help.
        This send a default page of help.

        .. versionadded:: 0.1
        """
        filtered: List[AnyCommand]
        if self.is_interaction_based():
            filtered = await self.filter_commands(self.context.bot.tree.get_commands(), sort=True)  # type: ignore

        else:
            filtered = await self.filter_commands(self.context.bot.commands, sort=True)

        self.pages = self.get_pages(filtered)
        self.current_page = 1

        bot_help: Embed = self.get_bot_help()
        view: HelpCommandView = HelpCommandView(page_length=len(self.pages), button_callback=self.switch_page)

        view.message = await self.get_destination().send(embed=bot_help, view=view)

    async def send_cog_help(self, cog: Cog) -> None:
        """|coro|

        This function is not implemented yet.

        .. versionadded:: 0.1
        """
        raise NotImplementedError('This function is not implemented yet.')

    async def send_group_help(self, group: Group[Any, Any, Any]) -> None:
        """|coro|

        Send a group help message.

        .. versionadded:: 0.1
        """
        prefix: Optional[str] = self.context.prefix
        group_help: Embed = Embed(
            title=f'{prefix}{group.qualified_name} {group.signature}',
            description=group.help,
            color=self.embed_color
        )
        filtered: List[AnyCommand] = await self.filter_commands(group.commands, sort=True)
        self.pages = self.get_pages(filtered)
        self.current_page = 1
        length: int = len(self.pages)
        group_help.set_footer(text=f'Page 1/{length}')
        for child in self.pages[0]:
            group_help.add_field(
                name=f'{prefix}{child.qualified_name} {group.signature}',
                value=child.short_doc,  # type: ignore
                inline=False
            )

        view: HelpCommandView = HelpCommandView(page_length=length, button_callback=self.switch_page)

        view.message = await self.get_destination().send(embed=group_help, view=view)

    async def send_command_help(self, command: AnyCommand) -> None:
        """|coro|

        Send a command help message.

        .. versionadded:: 0.1
        """
        prefix: Optional[str] = self.context.prefix
        cmd_help: Embed = Embed(
            title=f'{prefix}{command.qualified_name} {command.signature}',  # type: ignore
            description=command.help,  # type: ignore
            color=self.embed_color
        )
        if isinstance(command, Group):
            filtered: List[AnyCommand] = await self.filter_commands(command.commands, sort=True)
            for child in filtered:
                cmd_help.add_field(
                    name=f'{prefix}{child.qualified_name} {child.signature}',  # type: ignore
                    value=child.short_doc,  # type: ignore
                    inline=False
                )

        await self.get_destination().send(embed=cmd_help)

    async def filter_commands(  # type: ignore
            self,
            commands: Iterable[AnyCommand],
            *,
            sort: Optional[bool] = False
    ) -> List[AnyCommand]:
        """|coro|

        Filter or sort commands.

        If a command is message command, call :meth:`HelpCommand.filter_commands` .
        If it is slash command, do nothing or just sort commands.

        .. versionadded:: 0.1

        Parameters
        -----------
        commands: List[:class:`AnyCommand`]
            A list of commands.
        sort: Optional[:class:`bool`]
            Whether to sort the list of commands.

        Returns
        --------
        List[:class:`AnyCommand`]
            A list of commands.
        """
        try:
            return await super().filter_commands(commands, sort=sort)  # type: ignore

        except Exception:
            if sort:
                dic = dict(zip([cmd.name for cmd in commands], commands))
                return [i[1] for i in sorted(dic.items())]

            else:
                return commands  # type: ignore

    def get_destination(self) -> Context[Any]:  # type: ignore
        """Return `.context` .

        This is implemented only for compatibility.

        .. versionadded:: 0.1

        Returns
        --------
        :class:`Context`
        """
        return self.context

    def command_not_found(self, string: str) -> str:
        """|maybecoro|

        Return an error message for when the command is not found.

        .. versionadded:: 0.1

        Parameters
        -----------
        string: :class:`str`
            A command name which is not found.

        Returns
        --------
        :class:`str`
            An error message.
        """
        return super().command_not_found(string)

    def subcommand_not_found(self, command: AnyCommand, string: str) -> str:
        """|maybecoro|

        Return an error message for when the sub command is not found.

        .. versionadded:: 0.1

        Parameters
        -----------
        command: :class:`AnyCommand`
            A parent command.
        string: :class:`str`
            A sub command which is not found.

        Returns
        --------
        :class:`str`
            An error message.
        """
        return super().subcommand_not_found(command, string)  # type: ignore

    async def send_error_message(self, error: str) -> None:
        """|coro|

        Send an error message.

        .. versionadded:: 0.1

        Parameters
        -----------
        error: :class:`str`
            An error message.
        """
        err: Embed = Embed(title=error, color=Color.red())
        await self.get_destination().send(embed=err)

    @slash_command(name='help', description=locale_str(text['default_help_doc']))  # type: ignore
    @describe(
        cmd=locale_str(text['cmd_doc']),
        subcmd=locale_str(text['subcmd_doc'])
    )
    @rename(cmd=locale_str(text['cmd']), subcmd=locale_str(text['subcmd']))
    async def slash_help(self, interaction: Interaction, cmd: Optional[str] = None, subcmd: Optional[str] = None) -> None:
        """|coro|

        A help command entry for slash command.
        This emulates the behavior of the help command on message commands.

        .. versionadded:: 0.1

        Parameters
        -----------
        interaction: :class:`Interaction`
        cmd: Optional[:class:`str`]
            A command name.
        subcmd: Optional[:class:`str`]
            A sub command name.
        """
        self.context = await Context.from_interaction(interaction)
        param: Optional[str]

        if cmd is not None and subcmd is None:
            param = cmd

        elif cmd is not None and subcmd is not None:
            param = f'{cmd} {subcmd}'

        else:
            param = None

        await self.command_callback(self.context, command=param)
