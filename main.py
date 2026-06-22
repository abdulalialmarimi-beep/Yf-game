import asyncio
import discord
import subprocess
from discord.ext import commands
from config import TOKEN, PREFIX
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

print("TEST 123")

subprocess.run(["pip", "install", "motor"], check=True)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is running!')

    def log_message(self, *args):
        pass

def run_server():
    server = HTTPServer(("0.0.0.0", 8080), Handler)
    server.serve_forever()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents
)

@bot.event
async def on_ready():
    print(f"✅ البوت شغال الآن: {bot.user}")

async def load_cogs():
    cogs = [
        "cogs.test_cog",
        "cogs.hisab",
        "cogs.jam3",
        "cogs.mufrad",
        "cogs.kat",
        "cogs.as3ar",
        "cogs.rabt",
        "cogs.aks",
        "cogs.fak",
        "cogs.s7_5ata",
        "cogs.niqat"
    ]

    for cog in cogs:
        try:
            await bot.load_extension(cog)
            print(f"✅ Loaded: {cog}")
        except Exception as e:
            print(f"❌ Error loading {cog}: {e}")

async def main():
    threading.Thread(target=run_server, daemon=True).start()

    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
