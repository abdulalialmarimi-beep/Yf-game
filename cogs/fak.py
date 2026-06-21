import asyncio
import random
import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import io

active_games: dict[int, bool] = {}
BG_PATH = "bg.png"

WORDS = [
    "كتاب", "قلم", "بيت", "شجرة", "سيارة", "طائرة", "مدرسة", "مستشفى",
    "جبال", "بحيرة", "صحراء", "غابة", "نجمة", "قمر", "شمس", "سحابة",
    "أسد", "نمر", "فيل", "زرافة", "حصان", "جمل", "نسر", "دلفين",
    "تفاحة", "موزة", "عنب", "برتقال", "فراولة", "مانغو", "ليمون", "تمر",
    "خبز", "جبنة", "عسل", "زيتون", "ثلاجة", "غسالة", "تلفاز", "هاتف",
    "كرسي", "طاولة", "نافذة", "سجادة", "مرآة", "ساعة", "حقيبة", "نظارة",
    "مطار", "ميناء", "جسر", "نفق", "شارع", "ميدان", "حديقة", "ملعب",
    "رياضة", "سباحة", "ملاكمة", "فروسية", "كرة", "مباراة", "بطولة", "ميدالية",
    "شاعر", "روائي", "ممثل", "مغني", "رسام", "نحات", "مصور", "موسيقار",
    "طبيب", "مهندس", "معلم", "محامي", "قاضي", "شرطي", "جندي", "طيار",
    "ربيع", "صيف", "خريف", "شتاء", "صباح", "مساء", "فجر", "ظهيرة",
    "حريق", "زلزال", "بركان", "فيضان", "عاصفة", "برق", "رعد", "ثلج",
    "لغة", "كلمة", "جملة", "قصيدة", "رواية", "قصة", "مسرحية", "فيلم",
    "معدن", "ذهب", "فضة", "ألماس", "زمرد", "ياقوت", "لؤلؤ", "مرجان",
    "فرح", "حزن", "غضب", "خوف", "أمل", "شجاعة", "صبر", "كرم",
]

def scramble(word):
    chars = list(word)
    random.shuffle(chars)
    while ''.join(chars) == word and len(word) > 1:
        random.shuffle(chars)
    return ''.join(chars)

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

class FakCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="فك")
    async def fak(self, ctx):
        channel_id = ctx.channel.id
        if active_games.get(channel_id):
            await ctx.send("⚠️ هناك لعبة قيد التشغيل! انتظر حتى تنتهي.")
            return
        active_games[channel_id] = True
        try:
            answer = random.choice(WORDS)
            scrambled = scramble(answer)
            file = make_image("فك", scrambled)
            await ctx.send(file=file)
            def check(m):
                return m.channel.id == channel_id and not m.author.bot and m.content.strip() == answer
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
                await ctx.send(f"🔴 انتهى الوقت! لم يفز أحد. الكلمة كانت: **{answer}**")
        finally:
            active_games[channel_id] = False

async def setup(bot):
    await bot.add_cog(FakCog(bot))
