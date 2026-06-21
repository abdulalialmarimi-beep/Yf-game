import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import aiohttp
from points import get_points, transfer_points

class NiqatCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="فلوس")
    async def floos(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        pts = get_points(member.id)
        solo = pts["solo"]
        group = pts["group"]
        total = solo + group

        # تحميل صورة العضو
        async with aiohttp.ClientSession() as session:
            async with session.get(str(member.display_avatar.url)) as resp:
                avatar_data = await resp.read()

        # إنشاء الصورة
        W, H = 600, 750
        img = Image.new("RGBA", (W, H), (100, 100, 110, 255))
        draw = ImageDraw.Draw(img)

        try:
            font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 45)
            font_med = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        except:
            font_big = ImageFont.load_default()
            font_med = font_big

        GOLD = (255, 215, 0)
        WHITE = (255, 255, 255)
        GREEN_DARK = (60, 90, 60)
        SHADOW = (30, 30, 30)

        # خلفية علوية رمادية
        draw.rectangle([0, 0, W, 300], fill=(80, 80, 90))

        # صورة العضو في دائرة
        avatar_img = Image.open(io.BytesIO(avatar_data)).convert("RGBA")
        avatar_img = avatar_img.resize((160, 160))
        mask = Image.new("L", (160, 160), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse([0, 0, 160, 160], fill=255)
        avatar_circle = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
        avatar_circle.paste(avatar_img, mask=mask)

        # دائرة ذهبية
        circle_bg = Image.new("RGBA", (180, 180), (0, 0, 0, 0))
        circle_draw = ImageDraw.Draw(circle_bg)
        circle_draw.ellipse([0, 0, 179, 179], outline=GOLD, width=5)
        img.paste(circle_bg, (210, 50), circle_bg)
        img.paste(avatar_circle, (220, 60), avatar_circle)

        # اسم العضو
        name = member.display_name[:15]
        bbox = draw.textbbox((0, 0), name, font=font_big)
        nw = bbox[2] - bbox[0]
        draw.text(((W - nw) / 2, 240), name, font=font_big, fill=GOLD)

        # رسم البطاقات
        def draw_card(y, label, value):
            # خلفية البطاقة
            draw.rounded_rectangle([30, y, W-30, y+85], radius=15, fill=GREEN_DARK)
            draw.rounded_rectangle([30, y, W-30, y+85], radius=15, outline=GOLD, width=2)

            # الرقم يسار
            num_str = str(value)
            draw.text((60, y+22), num_str, font=font_big, fill=GOLD)

            # خط فاصل
            draw.line([(150, y+15), (150, y+70)], fill=GOLD, width=2)

            # النص يمين
            bbox = draw.textbbox((0, 0), label, font=font_med)
            lw = bbox[2] - bbox[0]
            draw.text((W - lw - 70, y+25), label, font=font_med, fill=WHITE)

            # نجمة
            draw.text((W-65, y+22), "⭐", font=font_med, fill=GOLD)

        draw_card(320, "نقاط الالعاب الفرديه", solo)
        draw_card(430, "نقاط الالعاب الجماعيه", group)
        draw_card(540, "نقاط مجموع الالعاب", total)

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
        success = transfer_points(ctx.author.id, member.id, amount)
        if success:
            await ctx.send(f"✅ تم تحويل **{amount}** نقطة من {ctx.author.mention} إلى {member.mention}!")
        else:
            await ctx.send(f"❌ ما عندك نقاط كافية!")

async def setup(bot):
    await bot.add_cog(NiqatCog(bot))
