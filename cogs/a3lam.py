import asyncio
import random
import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import io
import aiohttp
from points import add_solo_points

active_games: dict[int, bool] = {}
BG_PATH = "bg.png"

_BG_CACHE = None
def get_bg():
    global _BG_CACHE
    if _BG_CACHE is None:
        _BG_CACHE = Image.open(BG_PATH).convert("RGBA")
    return _BG_CACHE.copy()

# (اسم الدولة, كود العلم)
COUNTRIES = [
    ("السعودية", "sa"), ("مصر", "eg"), ("الإمارات", "ae"), ("الكويت", "kw"),
    ("قطر", "qa"), ("البحرين", "bh"), ("عُمان", "om"), ("اليمن", "ye"),
    ("العراق", "iq"), ("سوريا", "sy"), ("لبنان", "lb"), ("الأردن", "jo"),
    ("فلسطين", "ps"), ("ليبيا", "ly"), ("تونس", "tn"), ("الجزائر", "dz"),
    ("المغرب", "ma"), ("السودان", "sd"), ("الصومال", "so"), ("موريتانيا", "mr"),
    ("فرنسا", "fr"), ("ألمانيا", "de"), ("إيطاليا", "it"), ("إسبانيا", "es"),
    ("البرتغال", "pt"), ("هولندا", "nl"), ("بلجيكا", "be"), ("سويسرا", "ch"),
    ("النمسا", "at"), ("السويد", "se"), ("النرويج", "no"), ("الدنمارك", "dk"),
    ("فنلندا", "fi"), ("بولندا", "pl"), ("اليونان", "gr"), ("تركيا", "tr"),
    ("روسيا", "ru"), ("أوكرانيا", "ua"), ("إنجلترا", "gb"), ("أيرلندا", "ie"),
    ("الولايات المتحدة", "us"), ("كندا", "ca"), ("المكسيك", "mx"), ("البرازيل", "br"),
    ("الأرجنتين", "ar"), ("كولومبيا", "co"), ("بيرو", "pe"), ("تشيلي", "cl"),
    ("الصين", "cn"), ("اليابان", "jp"), ("كوريا الجنوبية", "kr"), ("الهند", "in"),
    ("باكستان", "pk"), ("إيران", "ir"), ("أفغانستان", "af"), ("إندونيسيا", "id"),
    ("ماليزيا", "my"), ("تايلاند", "th"), ("فيتنام", "vn"), ("الفلبين", "ph"),
    ("أستراليا", "au"), ("نيوزيلندا", "nz"), ("جنوب أفريقيا", "za"), ("نيجيريا", "ng"),
    ("كينيا", "ke"), ("إثيوبيا", "et"), ("غانا", "gh"), ("الكاميرون", "cm"),
    ("المملكة المتحدة", "gb"), ("إسرائيل", "il"), ("سنغافورة", "sg"), ("بنغلاديش", "bd"),
]

async def make_image(country_name: str, flag_code: str) -> discord.File:
    img = get_bg()
    draw = ImageDraw.Draw(img)
    W, H = img.size

    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
    except:
        font_title = ImageFont.load_default()

    GOLD = (255, 215, 0, 255)
    SHADOW = (0, 0, 0, 200)

    # كتابة "أعلام" في أقصى اليمين
    title = "أعلام"
    bbox = draw.textbbox((0, 0), title, font=font_title)
    tw = bbox[2] - bbox[0]
    tx = W - tw - 20
    ty = 20
    draw.text((tx+3, ty+3), title, font=font_title, fill=SHADOW)
    draw.text((tx, ty), title, font=font_title, fill=GOLD)

    # تحميل العلم
    flag_url = f"https://flagcdn.com/w320/{flag_code}.png"
    async with aiohttp.ClientSession() as session:
        async with session.get(flag_url) as resp:
            flag_data = await resp.read()

    flag_img = Image.open(io.BytesIO(flag_data)).convert("RGBA")

    # تكبير العلم
    flag_w = int(W * 0.7)
    flag_h = int(flag_w * flag_img.height / flag_img.width)
    flag_img = flag_img.resize((flag_w, flag_h))

    # وضع العلم في وسط الصورة
    fx = (W - flag_w) // 2
    fy = (H - flag_h) // 2
    img.paste(flag_img, (fx, fy), flag_img)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return discord.File(buf, filename="flag.png")

class A3lamCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="أعلام")
    async def a3lam(self, ctx):
        channel_id = ctx.channel.id
        if active_games.get(channel_id):
            await ctx.send("⚠️ هناك لعبة قيد التشغيل!")
            return
        active_games[channel_id] = True
        try:
            country_name, flag_code = random.choice(COUNTRIES)
            file = await make_image(country_name, flag_code)
            await ctx.send(file=file)

            def check(m):
                return m.channel.id == channel_id and not m.author.bot and m.content.strip() == country_name

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
                await add_solo_points(winner.id)
                await ctx.send(f"✅ إجابة صحيحة! {winner.mention} فاز بنقطة (+1)")
            else:
                await ctx.send(f"🔴 انتهى الوقت! الدولة كانت: **{country_name}**")
        finally:
            active_games[channel_id] = False

async def setup(bot):
    await bot.add_cog(A3lamCog(bot))
