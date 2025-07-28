import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
from pyngrok import ngrok

# 讀取 .env 檔案
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
OWNER_ID = int(os.getenv("OWNER_ID"))
PORT = int(os.getenv("PORT"))
NGROK_TOKEN = os.getenv("NGROK_AUTH_TOKEN", "")

def is_owner(ctx):
    return ctx.author.id == OWNER_ID

# 登入 ngrok（可選）
if NGROK_TOKEN:
    ngrok.set_auth_token(NGROK_TOKEN)

# 設定 Discord 機器人
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

current_tunnel = None

@bot.event
async def on_ready():
    print(f"✅ Bot 上線：{bot.user}")

@bot.command()
async def NgrokStart(ctx):
    if ctx.channel.id != CHANNEL_ID or not is_owner(ctx):
        return
    global current_tunnel
    if current_tunnel:
        await ctx.send(f"🔁 已啟動：{current_tunnel.public_url}")
        return
    try:
        current_tunnel = ngrok.connect(addr=PORT, proto="http")
        await ctx.send(f"✅ Ngrok 連線成功：{current_tunnel.public_url}")
    except Exception as e:
        await ctx.send(f"⚠️ 錯誤：{str(e)}")
@bot.command()
async def NgrokStop(ctx):
    if ctx.channel.id != CHANNEL_ID or not is_owner(ctx):
        return
    global current_tunnel
    if current_tunnel:
        ngrok.disconnect(current_tunnel.public_url)
        current_tunnel = None
        await ctx.send("🛑 已關閉 ngrok")
    else:
        await ctx.send("❌ 沒有啟動的 ngrok")
@bot.command()
async def Status(ctx):
    if ctx.channel.id != CHANNEL_ID or not is_owner(ctx):
        return
    global current_tunnel
    if current_tunnel:
        await ctx.send(f"🔗 目前 ngrok 正在運作：{current_tunnel.public_url}")
    else:
        await ctx.send("📴 沒有啟動的 ngrok 連線")    

bot.run(TOKEN)
