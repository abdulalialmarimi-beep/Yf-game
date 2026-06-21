import asyncio
import random
import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import io
import os

from config import EMBED_COLOR

active_games: dict[int, bool] = {}

BG_PATH = "bg.png"  # اسم الصورة الخضراء في الريبو

def make_image(text: str) -> discord.File:
    """يولد صورة بالخلفية الخضراء والنص في الوسط"""
    img = Image.open(BG_PATH).convert("RGBA")
    draw = ImageDraw.Draw(img)
    
    W, H = img.size

    # حاول تحمل خط عريض وكبير
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
    except:
        font = ImageFont.load_default()

    # احسب حجم النص عشان تحطه في الوسط
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    x = (W - text_w) / 2
    y = (H - text_h) / 2

    # ظل للنص عشان يكون واضح
    draw.text((x+3, y+3), text, font=font, fill=(0, 0, 0, 200))
    # النص الأبيض
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return discord.File(buf, filename="game.png")


class HisabCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="حساب")
    async def hisab(self, ctx: commands.Context):
        channel_id = ctx.channel.id

        if active_games.get(channel_id):
            await ctx.send("⚠️ هناك لعبة قيد التشغيل! انتظر حتى تنتهي.")
            return

        active_games[channel_id] = True

        try:
            num1 = random.randint(1, 99)
            num2 = random.randint(1, 99)
            correct_answer = num1 + num2

            text = f"🧮 حساب\n{num1} + {num2} = ؟\n⏱️ عندك 10 ثواني"
            file = make_image(text)
            await ctx.send(file=file)

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
                    f"✅ إجابة صحيحة! {winner.mention} فاز بنقطة واحدة (+1)"
                )
            else:
                await ctx.send(
                    f"🔴 انتهى الوقت! لم يفز أحد. الإجابة كانت: **{correct_answer}**"
                )

        finally:
            active_games[channel_id] = False


async def setup(bot: commands.Bot):
    await bot.add_cog(HisabCog(bot))
    
