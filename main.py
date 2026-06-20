import asyncio
import discord
from discord.ext import commands

from config import TOKEN, PREFIX

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)


@bot.event
async def on_ready():
    print(f"✅ البوت شغال الآن: {bot.user}")


async def load_cogs():
    await bot.load_extension("cogs.test_cog")


async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
