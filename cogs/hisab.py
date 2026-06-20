import asyncio
import random

import discord
from discord.ext import commands

from config import EMBED_COLOR

active_games: dict[int, bool] = {}


class HisabCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="حساب")
    async def hisab(self, ctx: commands.Context):
        channel_id = ctx.channel.id

        if active_games.get(channel_id):
            await ctx.send("⚠️ هناك لعبة قيد التشغيل بالفعل! انتظر حتى تنتهي.")
            return

        active_games[channel_id] = True

        try:
            num1 = random.randint(1, 99)
            num2 = random.randint(1, 99)
            correct_answer = num1 + num2

            embed = discord.Embed(
                title="حساب",
                description=f"**{num1} + {num2}**",
                color=EMBED_COLOR,
            )
            embed.set_footer(text="SOLOGAMES")
            await ctx.send(embed=embed)

            def check(message: discord.Message) -> bool:
                if message.channel.id != channel_id:
                    return False
                if message.author.bot:
                    return False
                return message.content.strip().lstrip("-").isdigit()

            end_time = asyncio.get_event_loop().time() + 10
            winner = None

            while True:
                remaining = end_time - asyncio.get_event_loop().time()
                if remaining <= 0:
                    break
                try:
                    msg = await self.bot.wait_for(
                        "message", timeout=remaining, check=check
                    )
                except asyncio.TimeoutError:
                    break

                if int(msg.content.strip()) == correct_answer:
                    winner = msg.author
                    break

            if winner:
                await ctx.send(
                    f"✅ إجابة صحيحة! {winner.mention} فاز بنقطة واحدة! (+1)"
                )
            else:
                await ctx.send(
                    f"⏰ انتهى الوقت! لم يفز أحد. الإجابة كانت: **{correct_answer}**"
                )

        finally:
            active_games[channel_id] = False


async def setup(bot: commands.Bot):
    await bot.add_cog(HisabCog(bot))
