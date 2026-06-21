import asyncio
import random
import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import io

active_games: dict[int, bool] = {}
BG_PATH = "bg.png"

QUESTIONS = [
    ("كبير", "صغير"), ("سريع", "بطيء"), ("قوي", "ضعيف"), ("جميل", "قبيح"),
    ("طويل", "قصير"), ("ثقيل", "خفيف"), ("حار", "بارد"), ("قديم", "جديد"),
    ("غني", "فقير"), ("صعب", "سهل"), ("نظيف", "وسخ"), ("مضيء", "مظلم"),
    ("فرح", "حزن"), ("حب", "كره"), ("سلام", "حرب"), ("نجاح", "فشل"),
    ("صحة", "مرض"), ("أمان", "خطر"), ("صدق", "كذب"), ("خير", "شر"),
    ("بداية", "نهاية"), ("دخول", "خروج"), ("صعود", "نزول"), ("تقدم", "تأخر"),
    ("فتح", "إغلاق"), ("نوم", "صحيان"), ("ضحك", "بكاء"), ("ذكاء", "غباء"),
    ("شجاعة", "جبن"), ("كرم", "بخل"), ("صبر", "تسرع"), ("أمانة", "خيانة"),
    ("وفاء", "غدر"), ("تواضع", "كبر"), ("رحمة", "قسوة"), ("عدل", "ظلم"),
    ("نور", "ظلام"), ("حرارة", "برودة"), ("جفاف", "رطوبة"), ("صمت", "ضجيج"),
    ("حركة", "سكون"), ("حياة", "موت"), ("أمل", "يأس"), ("راحة", "تعب"),
    ("شبع", "جوع"), ("ري", "عطش"), ("رضا", "سخط"), ("قبول", "رفض"),
    ("وصول", "رحيل"), ("لقاء", "فراق"), ("اتحاد", "فرقة"), ("تعاون", "تنافس"),
    ("قرب", "بعد"), ("أمام", "خلف"), ("فوق", "تحت"), ("يمين", "يسار"),
    ("داخل", "خارج"), ("أول", "أخير"), ("كثير", "قليل"), ("كل", "لا شيء"),
    ("دائم", "مؤقت"), ("ماضي", "مستقبل"), ("واقع", "خيال"), ("حقيقة", "وهم"),
    ("أصل", "فرع"), ("رئيسي", "ثانوي"), ("عام", "خاص"), ("مفتوح", "مغلق"),
    ("حاضر", "غائب"), ("موجود", "مفقود"), ("معروف", "مجهول"), ("واضح", "غامض"),
    ("بسيط", "معقد"), ("طبيعي", "اصطناعي"), ("أصيل", "مقلد"), ("أصلي", "زائف"),
    ("عميق", "سطحي"), ("واسع", "ضيق"), ("مستقيم", "معوج"), ("ناعم", "خشن"),
    ("صاخب", "هادئ"), ("مشرق", "معتم"), ("حديث", "قديم"), ("شمال", "جنوب"),
    ("شرق", "غرب"), ("ربح", "خسارة"), ("صحيح", "خاطئ"), ("مؤلم", "لذيذ"),
    ("رطب", "جاف"), ("مالح", "حلو"), ("حامض", "حلو"), ("مر", "حلو"),
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

class AksCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="عكس")
    async def aks(self, ctx):
        channel_id = ctx.channel.id
        if active_games.get(channel_id):
            await ctx.send("⚠️ هناك لعبة قيد التشغيل! انتظر حتى تنتهي.")
            return
        active_games[channel_id] = True
        try:
            word, answer = random.choice(QUESTIONS)
            file = make_image("عكس", word)
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
                await ctx.send(f"🔴 انتهى الوقت! لم يفز أحد. الإجابة كانت: **{answer}**")
        finally:
            active_games[channel_id] = False

async def setup(bot):
    await bot.add_cog(AksCog(bot))
