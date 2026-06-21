import asyncio
import random
import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap

active_games: dict[int, bool] = {}
BG_PATH = "bg.png"

# (جملة, الجواب الصحيح)
QUESTIONS = [
    ("الشمس تشرق من الشرق", "صح"),
    ("القمر كوكب", "خطأ"),
    ("الماء يغلي عند 100 درجة", "صح"),
    ("الأرض مسطحة", "خطأ"),
    ("الإنسان يتنفس الأكسجين", "صح"),
    ("السمك يعيش في البر", "خطأ"),
    ("النخلة شجرة", "صح"),
    ("الثلج حار", "خطأ"),
    ("الذهب معدن", "صح"),
    ("الطائرة تسير على الماء", "خطأ"),
    ("باريس عاصمة فرنسا", "صح"),
    ("طوكيو عاصمة الصين", "خطأ"),
    ("النيل أطول نهر في العالم", "صح"),
    ("المحيط الهادئ أصغر المحيطات", "خطأ"),
    ("الزرافة أطول الحيوانات", "صح"),
    ("الفيل أسرع حيوان في العالم", "خطأ"),
    ("الفهد أسرع حيوان في العالم", "صح"),
    ("الحوت الأزرق أضخم حيوان", "صح"),
    ("القرآن الكريم 114 سورة", "صح"),
    ("رمضان 31 يوم", "خطأ"),
    ("الصلوات اليومية 5", "صح"),
    ("أركان الإسلام 6", "خطأ"),
    ("مكة في السعودية", "صح"),
    ("المدينة المنورة في مصر", "خطأ"),
    ("الكعبة المشرفة في مكة", "صح"),
    ("الرياض عاصمة الإمارات", "خطأ"),
    ("أبوظبي عاصمة الإمارات", "صح"),
    ("دبي عاصمة الإمارات", "خطأ"),
    ("الكويت دولة خليجية", "صح"),
    ("قطر جزيرة كبيرة", "خطأ"),
    ("السنة 12 شهر", "صح"),
    ("الأسبوع 8 أيام", "خطأ"),
    ("اليوم 24 ساعة", "صح"),
    ("الساعة 100 دقيقة", "خطأ"),
    ("الدقيقة 60 ثانية", "صح"),
    ("المشتري أكبر كوكب", "صح"),
    ("عطارد أبعد كوكب عن الشمس", "خطأ"),
    ("الأرض تدور حول الشمس", "صح"),
    ("الشمس تدور حول الأرض", "خطأ"),
    ("للإنسان 5 حواس", "صح"),
    ("الدم لون أزرق", "خطأ"),
    ("القلب يضخ الدم", "صح"),
    ("الرئتان للهضم", "خطأ"),
    ("المعدة للهضم", "صح"),
    ("الدماغ في الصدر", "خطأ"),
    ("الجلد أكبر أعضاء الجسم", "صح"),
    ("العظام مصنوعة من الجلد", "خطأ"),
    ("الإنسان عنده 206 عظمة", "صح"),
    ("الأسنان اللبنية 32 سن", "خطأ"),
    ("للإنسان 10 أصابع في اليدين", "صح"),
    ("إيفرست أعلى جبل في العالم", "صح"),
    ("الصحراء الكبرى في أوروبا", "خطأ"),
    ("أفريقيا قارة", "صح"),
    ("أستراليا دولة وقارة", "صح"),
    ("القطب الشمالي في الجنوب", "خطأ"),
    ("الجليد ماء متجمد", "صح"),
    ("البخار ماء ساخن", "صح"),
    ("المطر يأتي من الأرض", "خطأ"),
    ("السحاب يحمل المطر", "صح"),
    ("الرعد قبل البرق", "خطأ"),
    ("الضوء أسرع من الصوت", "صح"),
    ("الصوت أسرع من الضوء", "خطأ"),
    ("النباتات تصنع غذاءها", "صح"),
    ("الحيوانات تتنفس ثاني أكسيد الكربون", "خطأ"),
    ("الأوكسجين ضروري للتنفس", "صح"),
    ("الماء H2O", "صح"),
    ("الذهب يصدأ", "خطأ"),
    ("الحديد يصدأ", "صح"),
    ("الألماس أصلب المواد", "صح"),
    ("الزجاج يمتص الضوء", "خطأ"),
    ("المرآة تعكس الضوء", "صح"),
    ("الألوان الأساسية 4", "خطأ"),
    ("الألوان الأساسية 3", "صح"),
    ("قوس قزح 7 ألوان", "صح"),
    ("الليمون حلو الطعم", "خطأ"),
    ("الملح مالح", "صح"),
    ("السكر مر", "خطأ"),
    ("العسل حلو", "صح"),
    ("الخل حامض", "صح"),
    ("الفلفل الحار بارد", "خطأ"),
    ("القهوة تحتوي على كافيين", "صح"),
    ("الشاي الأخضر مفيد للصحة", "صح"),
    ("الماء البارد يطفئ العطش", "صح"),
    ("تناول الخضروات مفيد", "صح"),
    ("النوم الكافي مهم للصحة", "صح"),
    ("التدخين مفيد للصحة", "خطأ"),
    ("الرياضة تقوي الجسم", "صح"),
    ("الإفراط في السكر ضار", "صح"),
    ("شرب الماء الكافي مهم", "صح"),
    ("الفيتامينات ضرورية للجسم", "صح"),
    ("الكالسيوم يقوي العظام", "صح"),
    ("الحديد يقوي الدم", "صح"),
    ("فيتامين C في الليمون", "صح"),
    ("فيتامين D من الشمس", "صح"),
    ("البروتين يبني العضلات", "صح"),
    ("الدهون كلها ضارة", "خطأ"),
    ("الألياف مفيدة للهضم", "صح"),
    ("الضغط العالي خطير", "صح"),
    ("السكري مرض مزمن", "صح"),
]

def make_image(question: str) -> discord.File:
    img = Image.open(BG_PATH).convert("RGBA")
    draw = ImageDraw.Draw(img)
    W, H = img.size
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 90)
        font_q = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 65)
    except:
        font_title = ImageFont.load_default()
        font_q = font_title

    GOLD = (255, 215, 0, 255)
    SHADOW = (0, 0, 0, 200)

    title = "صح أم خطأ؟"
    bbox = draw.textbbox((0, 0), title, font=font_title)
    tw = bbox[2] - bbox[0]
    tx = (W - tw) / 2
    ty = H * 0.1
    draw.text((tx+3, ty+3), title, font=font_title, fill=SHADOW)
    draw.text((tx, ty), title, font=font_title, fill=GOLD)

    lines = textwrap.wrap(question, width=22)
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


class S7KhataCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="صح")
    async def s7_5ata(self, ctx):
        channel_id = ctx.channel.id
        if active_games.get(channel_id):
            await ctx.send("⚠️ هناك لعبة قيد التشغيل! انتظر حتى تنتهي.")
            return
        active_games[channel_id] = True
        try:
            question, answer = random.choice(QUESTIONS)
            file = make_image(question)
            await ctx.send(file=file)

            def check(m):
                return m.channel.id == channel_id and not m.author.bot and m.content.strip() in ["صح", "خطأ", "خطا"]

            end_time = asyncio.get_event_loop().time() + 10
            winner = None

            while True:
                remaining = end_time - asyncio.get_event_loop().time()
                if remaining <= 0:
                    break
                try:
                    msg = await self.bot.wait_for("message", timeout=remaining, check=check)
                    user_answer = msg.content.strip()
                    if user_answer == answer or (user_answer == "خطا" and answer == "خطأ"):
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
    await bot.add_cog(S7KhataCog(bot))
