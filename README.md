# Discord Bot

A simple Discord bot template built with discord.py.

## Setup

1. Clone this repository
2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
5. Edit `.env` and add your Discord bot token
6. Run the bot:
   ```bash
   python bot.py
   ```

## Features

- Basic bot structure with event handlers
- Command handling using the `!` prefix
- Environment variable configuration
- Simple ping command for testing

## Available Commands

- `!ping`: Check if the bot is responsive and view latency

## Adding New Commands

To add new commands, create functions with the `@bot.command()` decorator in `bot.py`:

```python
@bot.command(name='command_name')
async def command_name(ctx):
    await ctx.send('Command response')
```
