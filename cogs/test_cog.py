import discord
from discord.ext import commands
from config import EMBED_COLOR


class TestCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="تجربة")
    async def test_embed(self, ctx: commands.Context):
        embed = discord.Embed(
            title="حساب",
            description="**15 + 91**",
            color=EMBED_COLOR,
        )
        embed.set_footer(text="SOLOGAMES")
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(TestCog(bot))
