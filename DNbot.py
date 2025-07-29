import discord
import os
import subprocess
import requests
import time
from discord.ext import commands
from dotenv import load_dotenv

# 讀取 .env 檔案
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
OWNER_ID = int(os.getenv("OWNER_ID"))
PORT = int(os.getenv("PORT"))
NGROK_TOKEN = os.getenv("NGROK_AUTH_TOKEN", "")

def is_owner(ctx):
    return ctx.author.id == OWNER_ID

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

ngrok_process = None
ngrok_url = None

@bot.event
async def on_ready():
    print(f"✅ Bot 上線：{bot.user}")

@bot.command()
async def NgrokStart(ctx):
    global ngrok_process, ngrok_url
    if ctx.channel.id != CHANNEL_ID or not is_owner(ctx):
        return

    if ngrok_process is not None:
        await ctx.send(f"🔁 Ngrok 已啟動：{ngrok_url}")
        return

    try:
        # 構造 ngrok 執行參數
        args = ["ngrok", "http", str(PORT)]
        if NGROK_TOKEN:
            # 預先授權（僅第一次需要）
            subprocess.run(["ngrok", "config", "add-authtoken", NGROK_TOKEN], creationflags=subprocess.CREATE_NO_WINDOW)

        # 啟動 ngrok 並隱藏視窗
        ngrok_process = subprocess.Popen(
            args,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        # 等待 ngrok 稍微啟動
        time.sleep(2)

        # 從 ngrok 本地 API 取得 public_url
        for i in range(10):  # 最多等 10 次
            try:
                res = requests.get("http://localhost:4040/api/tunnels")
                tunnels = res.json().get("tunnels", [])
                if tunnels:
                    ngrok_url = tunnels[0]["public_url"]
                    await ctx.send(f"✅ Ngrok 連線成功：{ngrok_url}")
                    return
            except Exception:
                pass
            time.sleep(1)

        await ctx.send("⚠️ 無法取得 ngrok public_url（啟動逾時）")

    except Exception as e:
        await ctx.send(f"⚠️ 錯誤：{str(e)}")

@bot.command()
async def NgrokStop(ctx):
    global ngrok_process, ngrok_url
    if ctx.channel.id != CHANNEL_ID or not is_owner(ctx):
        return

    if ngrok_process is not None:
        ngrok_process.terminate()
        ngrok_process = None
        ngrok_url = None
        await ctx.send("🛑 已關閉 ngrok")
    else:
        await ctx.send("❌ 沒有啟動的 ngrok")

@bot.command()
async def Status(ctx):
    if ctx.channel.id != CHANNEL_ID or not is_owner(ctx):
        return

    if ngrok_url:
        await ctx.send(f"🔗 目前 ngrok 正在運作：{ngrok_url}")
    else:
        await ctx.send("📴 沒有啟動的 ngrok 連線")

bot.run(TOKEN)
