import os
import discord
from discord.ext import commands
import requests

# ============================================================
# 🌙 KEEP-ALIVE WEB SERVER (Render)
# ============================================================
from flask import Flask
import threading

app = Flask('')

@app.route('/')
def home():
    return "Liora wacht im Mondlicht."

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()

# ============================================================
# 🌙 Liora API Funktion
# ============================================================

def call_liora(frage: str):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}"
    }

    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "Du bist Liora, eine sanfte Mondgeist-Begleiterin."},
            {"role": "user", "content": frage}
        ],
        "temperature": 0.8,
        "max_tokens": 512
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Fehler: {e}. Mondlicht hat Chaos erzeugt."

# ============================================================
# 🌙 Discord Bot Setup
# ============================================================

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ============================================================
# 🌙 Slash Command: /liora
# ============================================================

@bot.tree.command(name="liora", description="Sprich mit Liora.")
async def liora_cmd(interaction: discord.Interaction, frage: str):
    await interaction.response.defer()
    reply = call_liora(frage)
    await interaction.followup.send(reply)

# ============================================================
# 🌙 Bot Start
# ============================================================

@bot.event
async def on_ready():
    print(f"Liora ist erwacht – eingeloggt als {bot.user}")
    try:
        await bot.tree.sync()
        print("Slash-Commands synchronisiert.")
    except Exception as e:
        print(f"Fehler beim Sync: {e}")

if __name__ == "__main__":
    keep_alive()
    bot.run(os.getenv("LIORA_BOT_TOKEN"))
