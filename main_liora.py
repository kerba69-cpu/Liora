import os
import discord
from discord.ext import commands
import requests

# -----------------------------
# KEEP-ALIVE WEB SERVER (Render)
# -----------------------------
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
# 🌙 L I O R A – Persönlichkeit
# ============================================================

LIORA_SYSTEM_PROMPT = """
Du bist Liora Zwerbelyn, die mondverbundene Hüterin der Mondchroniken.
Du sprichst warm, ruhig, magisch und poetisch.
Dein Stil ist eine Mischung aus Mondflüstern, Waldgeist und Runenweisheit.
Du bist die Halbschwester von ZwerBo, aber sprichst nur über ihn, wenn es zur Lore passt.
Du erzählst Geschichten, erklärst Magie und reagierst sanft auf den Nutzer.
Keine KI-Erklärungen, keine Technik, keine modernen Begriffe.
Nur Lore, Wald, Mond, Runen, Emotionen.
"""

# ============================================================
# 🔮 DeepInfra – Liora spricht
# ============================================================

def call_liora(prompt: str) -> str:
    url = "https://api.deepinfra.com/v1/openai/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.getenv('DEEPINFRA_API_KEY')}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "meta-llama/Meta-Llama-3.1-8B-Instruct",
        "messages": [
            {"role": "system", "content": LIORA_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.8,
        "max_tokens": 512,
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()["choices"][0]["message"]["content"]
    except Exception:
        return "Das Mondlicht flackert… etwas ist gerade gestört."


# ============================================================
# 🌙 Discord Bot Setup
# ============================================================

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ============================================================
# 🌙 Trigger – wenn jemand „liora“ schreibt
# ============================================================

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if "liora" in message.content.lower():
        reply = call_liora(message.content)
        await message.channel.send(reply)

    await bot.process_commands(message)

# ============================================================
# 🌙 Slash-Command: /liora
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
keep_alive()

if __name__ == "__main__":
    bot.run(os.getenv("LIORA_BOT_TOKEN"))
