import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import io
import aiohttp

PROFILE_BG = "profile.png"

class NiqatCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="فلوس")
    async def floos(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        solo = 0
        group = 0
        total = 0

        async with aiohttp.ClientSession() as session:
            async with session.get(str(member.display_avatar.url)) as resp:
                avatar_data = await resp.read()

        img = Image.open(PROFILE_BG).convert("RGBA")
        draw = ImageDraw.Draw(img)
        W, H = img.size

        try:
            font_num = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 55)
        except:
            font_num = ImageFont.load_default()

        GOLD = (255, 215, 0, 255)
        SHADOW = (0, 0, 0, 200)

        avatar_img = Image.open(io.BytesIO(avatar_data)).convert("RGBA")
        avatar_img = avatar_img.resize((190, 190))
        mask = Image.new("L", (190, 190), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse([0, 0, 190, 190], fill=255)
        avatar_circle = Image.new("RGBA", (190, 190), (0, 0, 0, 0))
        avatar_circle.paste(avatar_img, mask=mask)

        ax = (W - 190) // 2
        ay = int(H * 0.08)
        img.paste(avatar_circle, (ax, ay), avatar_circle)

        y1 = int(H * 0.57)
        y2 = int(H * 0.71)
        y3 = int(H * 0.85)

        for val, y in [(solo, y1), (group, y2), (total, y3)]:
            num_str = str(val)
            x = int(W * 0.15)
            draw.text((x+2, y+2), num_str, font=font_num, fill=SHADOW)
            draw.text((x, y), num_str, font=font_num, fill=GOLD)

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        await ctx.send(file=discord.File(buf, filename="floos.png"))

    @commands.command(name="تحويل")
    async def tahweel(self, ctx, member: discord.Member, amount: int):
        if amount <= 0:
            await ctx.send("❌ الرقم لازم يكون أكبر من 0!")
            return
        if member.id == ctx.author.id:
            await ctx.send("❌ ما تقدر تحول لنفسك!")
            return
        await ctx.send("⚠️ نظام النقاط قيد التطوير!")

async def setup(bot):
    await bot.add_cog(NiqatCog(bot))
