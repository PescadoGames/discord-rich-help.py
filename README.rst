discord-rich-help.py
====================

.. image:: https://img.shields.io/pypi/v/discord-rich-help.py.svg
   :target: https://pypi.python.org/pypi/discord-rich-help.py
   :alt: PyPI version info
.. image:: https://img.shields.io/pypi/pyversions/discord-rich-help.py.svg
   :target: https://pypi.python.org/pypi/discord-rich-help.py
   :alt: PyPI supported Python versions

An extension which makes a rich-help command for discord.py

Key Features
-------------

- Supports both message and slash commands.

Installing
-----------

**Python 3.8 or higher is required**

.. code:: sh

    # Linux/MacOS
    python3 -m pip install -U discord-rich-help.py

    # Windows
    py -3 -m pip install -U discord-rich-help.py

Bot Example
~~~~~~~~~~~~

.. code:: py

    import discord
    from discord.ext import commands
    from discord_rich_help import RichHelpCommand

    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix='?', intents=intents, help_command=RichHelpCommand())

    bot.run('token')

Links
------

- `Documentation <https://github.com/PescadoGames/discord-rich-help.py/wiki>`_
- `discord.py <https://pypi.python.org/pypi/discord.py>`_
