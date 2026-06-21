import asyncio
import random
import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap

active_games: dict[int, bool] = {}
BG_PATH = "bg.png"

# (سؤال, جواب)
QUESTIONS = [
    ("عاصمة فرنسا", "باريس"),
    ("عاصمة اليابان", "طوكيو"),
    ("عاصمة البرازيل", "برازيليا"),
    ("عاصمة أستراليا", "كانبيرا"),
    ("عاصمة كندا", "أوتاوا"),
    ("عاصمة مصر", "القاهرة"),
    ("عاصمة السعودية", "الرياض"),
    ("عاصمة الإمارات", "أبوظبي"),
    ("عاصمة الكويت", "الكويت"),
    ("عاصمة قطر", "الدوحة"),
    ("عاصمة البحرين", "المنامة"),
    ("عاصمة عُمان", "مسقط"),
    ("عاصمة اليمن", "صنعاء"),
    ("عاصمة العراق", "بغداد"),
    ("عاصمة سوريا", "دمشق"),
    ("عاصمة لبنان", "بيروت"),
    ("عاصمة الأردن", "عمّان"),
    ("عاصمة فلسطين", "القدس"),
    ("عاصمة ليبيا", "طرابلس"),
    ("عاصمة تونس", "تونس"),
    ("عاصمة الجزائر", "الجزائر"),
    ("عاصمة المغرب", "الرباط"),
    ("عاصمة السودان", "الخرطوم"),
    ("عاصمة الصومال", "مقديشو"),
    ("عاصمة إثيوبيا", "أديس أبابا"),
    ("عاصمة كينيا", "نيروبي"),
    ("عاصمة نيجيريا", "أبوجا"),
    ("عاصمة جنوب أفريقيا", "بريتوريا"),
    ("عاصمة الهند", "نيودلهي"),
    ("عاصمة الصين", "بكين"),
    ("عاصمة روسيا", "موسكو"),
    ("عاصمة ألمانيا", "برلين"),
    ("عاصمة إيطاليا", "روما"),
    ("عاصمة إسبانيا", "مدريد"),
    ("عاصمة البرتغال", "لشبونة"),
    ("عاصمة هولندا", "أمستردام"),
    ("عاصمة بلجيكا", "بروكسل"),
    ("عاصمة سويسرا", "برن"),
    ("عاصمة النمسا", "فيينا"),
    ("عاصمة السويد", "ستوكهولم"),
    ("عاصمة النرويج", "أوسلو"),
    ("عاصمة الدنمارك", "كوبنهاغن"),
    ("عاصمة فنلندا", "هلسنكي"),
    ("عاصمة بولندا", "وارسو"),
    ("عاصمة اليونان", "أثينا"),
    ("عاصمة تركيا", "أنقرة"),
    ("عاصمة إيران", "طهران"),
    ("عاصمة أفغانستان", "كابول"),
    ("عاصمة باكستان", "إسلام آباد"),
    ("عاصمة بنغلاديش", "دكا"),
    ("عاصمة إندونيسيا", "جاكرتا"),
    ("عاصمة ماليزيا", "كوالالمبور"),
    ("عاصمة تايلاند", "بانكوك"),
    ("عاصمة فيتنام", "هانوي"),
    ("عاصمة كوريا الجنوبية", "سيول"),
    ("عاصمة كوريا الشمالية", "بيونغ يانغ"),
    ("عاصمة المكسيك", "مكسيكو سيتي"),
    ("عاصمة الأرجنتين", "بوينس آيرس"),
    ("عاصمة كولومبيا", "بوغوتا"),
    ("عاصمة بيرو", "ليما"),
    ("عاصمة تشيلي", "سانتياغو"),
    ("أطول نهر في العالم", "النيل"),
    ("أعلى جبل في العالم", "إيفرست"),
    ("أكبر محيط في العالم", "المحيط الهادئ"),
    ("أكبر صحراء في العالم", "الصحراء الكبرى"),
    ("أكبر دولة في العالم", "روسيا"),
    ("أصغر دولة في العالم", "الفاتيكان"),
    ("أكثر دولة سكاناً في العالم", "الهند"),
    ("أعمق بحيرة في العالم", "بايكال"),
    ("أكبر جزيرة في العالم", "غرينلاند"),
    ("أطول سور في العالم", "سور الصين العظيم"),
    ("لون السماء", "أزرق"),
    ("لون الذهب", "أصفر"),
    ("لون الدم", "أحمر"),
    ("لون النباتات", "أخضر"),
    ("لون الثلج", "أبيض"),
    ("لون الليل", "أسود"),
    ("كوكب الحلقات", "زحل"),
    ("أقرب كوكب للشمس", "عطارد"),
    ("أكبر كوكب في المجموعة الشمسية", "المشتري"),
    ("الكوكب الأحمر", "المريخ"),
    ("عدد أيام السنة", "365"),
    ("عدد أشهر السنة", "12"),
    ("عدد أيام الأسبوع", "7"),
    ("عدد ساعات اليوم", "24"),
    ("عدد دقائق الساعة", "60"),
    ("عدد ثواني الدقيقة", "60"),
    ("عدد أركان الإسلام", "5"),
    ("عدد الصلوات اليومية", "5"),
    ("عدد أيام رمضان", "30"),
    ("أول خليفة في الإسلام", "أبوبكر الصديق"),
    ("عدد سور القرآن الكريم", "114"),
    ("أطول سورة في القرآن", "البقرة"),
    ("أقصر سورة في القرآن", "الكوثر"),
    ("عاصمة إنجلترا", "لندن"),
    ("عاصمة أمريكا", "واشنطن"),
    ("أكبر مدينة في العالم", "طوكيو"),
    ("مخترع الهاتف", "غراهام بيل"),
    ("مخترع الكهرباء", "توماس إديسون"),
    ("أسرع حيوان في العالم", "الفهد"),
    ("أضخم حيوان في العالم", "الحوت الأزرق"),
    ("أطول حيوان في العالم", "الزرافة"),
]

def make_image(question: str) -> discord.File:
    img = Image.open(BG_PATH).convert("RGBA")
    draw = ImageDraw.Draw(img)
    W, H = img.size

    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 90)
        font_q = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 70)
    except:
        font_title = ImageFont.load_default()
        font_q = font_title

    GOLD = (255, 215, 0, 255)
    SHADOW = (0, 0, 0, 200)

    title = "ربط"
    bbox = draw.textbbox((0, 0), title, font=font_title)
    tw = bbox[2] - bbox[0]
    tx = (W - tw) / 2
    ty = H * 0.1
    draw.text((tx+3, ty+3), title, font=font_title, fill=SHADOW)
    draw.text((tx, ty), title, font=font_title, fill=GOLD)

    lines = textwrap.wrap(question, width=20)
    total_h = sum([draw.textbbox((0,0), l, font=font_q)[3] - draw.textbbox((0,0), l, font=font_q)[1] + 10 for l in lines])
    y = (H - total_h) / 2

    for line in lines:
        bbox2 = draw.textbbox((0, 0), line, font=font_q)
        lw = bbox2[2] - bbox2[0]
        lh = bbox2[3] - bbox2[1]
        x = (W - lw) / 2
        draw.text((x+3, y+3), line, font=font_q, fill=SHADOW)
        draw.text((x, y), line, font=font_q, fill=GOLD)
        y += lh + 10

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return discord.File(buf, filename="game.png")


class RabtCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="ربط")
    async def rabt(self, ctx: commands.Context):
        channel_id = ctx.channel.id

        if active_games.get(channel_id):
            await ctx.send("⚠️ هناك لعبة قيد التشغيل! انتظر حتى تنتهي.")
            return

        active_games[channel_id] = True

        try:
            question, answer = random.choice(QUESTIONS)
            file = make_image(question)
            await ctx.send(file=file)

            def check(message: discord.Message) -> bool:
                if message.channel.id != channel_id:
                    return False
                if message.author.bot:
                    return False
                return message.content.strip() == answer

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


async def setup(bot: commands.Bot):
    await bot.add_cog(RabtCog(bot))
