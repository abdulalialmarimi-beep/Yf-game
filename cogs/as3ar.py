import asyncio
import random
import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import io

active_games: dict[int, bool] = {}
BG_PATH = "bg.png"

WORDS = [
    "نجم", "قمر", "شمس", "بحر", "جبل", "نهر", "ريح", "برق", "رعد", "ثلج",
    "ورد", "نخل", "غاب", "صحر", "واد", "جزر", "شاط", "صخر", "رمل", "تراب",
    "أسد", "نمر", "فيل", "ذئب", "ثعل", "غزال", "حصان", "جمل", "نسر", "صقر",
    "تفاح", "موز", "عنب", "تمر", "ليمون", "خوخ", "مانغو", "فراول", "بطيخ", "شمام",
    "خبز", "لحم", "سمك", "بيض", "لبن", "جبن", "عسل", "زيت", "ملح", "سكر",
    "كتاب", "قلم", "ورقة", "مكتب", "كرسي", "طاولة", "سبورة", "حقيبة", "دفتر", "مسطرة",
    "هاتف", "حاسوب", "شاشة", "طابعة", "كاميرا", "تلفاز", "راديو", "ثلاجة", "غسالة", "مكيف",
    "سيارة", "طائرة", "قطار", "باخرة", "دراجة", "حافلة", "مترو", "تاكسي", "شاحنة", "جرار",
    "مسجد", "مدرسة", "مستشفى", "متجر", "مطعم", "فندق", "متحف", "مكتبة", "ملعب", "مسبح",
    "جبال", "غابة", "صحراء", "بحيرة", "محيط", "جزيرة", "شاطئ", "وادي", "سهل", "هضبة",
    "ذهب", "فضة", "نحاس", "حديد", "ألماس", "زمرد", "ياقوت", "لؤلؤ", "عقيق", "مرجان",
    "فرح", "حزن", "غضب", "خوف", "أمل", "حب", "كره", "عجب", "فخر", "خجل",
    "صديق", "عدو", "أخ", "أخت", "أب", "أم", "جد", "جدة", "عم", "خال",
    "ملك", "أمير", "وزير", "رئيس", "قاضي", "شرطي", "جندي", "طبيب", "معلم", "مهندس",
    "قصيدة", "رواية", "قصة", "مسرحية", "فيلم", "أغنية", "لوحة", "تمثال", "نشيد", "ملحمة",
    "كرة", "سباحة", "جري", "ملاكمة", "مصارعة", "رماية", "فروسية", "تنس", "غولف", "سكواش",
    "ربيع", "صيف", "خريف", "شتاء", "صباح", "ظهر", "مساء", "ليل", "فجر", "عصر",
    "حريق", "فيضان", "زلزال", "بركان", "عاصفة", "جفاف", "صقيع", "ضباب", "عواصف", "موجة",
    "لغة", "كلمة", "جملة", "فقرة", "قصة", "رواية", "شعر", "نثر", "خطاب", "رسالة",
    "علم", "فيزياء", "كيمياء", "أحياء", "رياضيات", "تاريخ", "جغرافيا", "فلسفة", "منطق", "نفس",
]

def make_image(title: str, question: str) -> discord.File:
    img = Image.open(BG_PATH).convert("RGBA")
    draw = ImageDraw.Draw(img)
    W, H = img.size

    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 90)
        font_question = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 100)
    except:
        font_title = ImageFont.load_default()
        font_question = font_title

    GOLD = (255, 215, 0, 255)
    SHADOW = (0, 0, 0, 200)

    bbox = draw.textbbox((0, 0), title, font=font_title)
    tw = bbox[2] - bbox[0]
    tx = (W - tw) / 2
    ty = H * 0.2
    draw.text((tx+3, ty+3), title, font=font_title, fill=SHADOW)
    draw.text((tx, ty), title, font=font_title, fill=GOLD)

    bbox2 = draw.textbbox((0, 0), question, font=font_question)
    qw = bbox2[2] - bbox2[0]
    qx = (W - qw) / 2
    qy = H * 0.5
    draw.text((qx+3, qy+3), question, font=font_question, fill=SHADOW)
    draw.text((qx, qy), question, font=font_question, fill=GOLD)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return discord.File(buf, filename="game.png")


class As3arCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="أسرع")
    async def as3ar(self, ctx: commands.Context):
        channel_id = ctx.channel.id

        if active_games.get(channel_id):
            await ctx.send("⚠️ هناك لعبة قيد التشغيل! انتظر حتى تنتهي.")
            return

        active_games[channel_id] = True

        try:
            word = random.choice(WORDS)
            file = make_image("أسرع", word)
            await ctx.send(file=file)

            def check(message: discord.Message) -> bool:
                if message.channel.id != channel_id:
                    return False
                if message.author.bot:
                    return False
                return message.content.strip() == word

            end_time = asyncio.get_event_loop().time() + 10
            winner = None

            while True:
                remaining = end_time - asyncio.get_event_loop().time()
                if remaining <= 0:
                    break
                try:
                    msg = await self.bot.wait_for("message", timeout=remaining, check=check)
                    winner = msg.author
                    break
                except asyncio.TimeoutError:
                    break

            if winner:
                await ctx.send(f"✅ إجابة صحيحة! {winner.mention} فاز بنقطة واحدة (+1)")
            else:
                await ctx.send(f"🔴 انتهى الوقت! لم يفز أحد. الكلمة كانت: **{word}**")

        finally:
            active_games[channel_id] = False


async def setup(bot: commands.Bot):
    await bot.add_cog(As3arCog(bot))
