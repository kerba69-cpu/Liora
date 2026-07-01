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
# 🌙 DeepInfra API Funktion
# ============================================================

def call_liora(frage: str):
    url = "https://api.deepinfra.com/v1/openai/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('DEEPINFRA_API_KEY')}"
    }

    data = {
        "model": "meta-llama/Meta-Llama-3-8B-Instruct",
        "messages": [
            {"role": "system", "content": "Du bist Liora. Du antwortest freundlich, klar und kurz. Du bist ein Mondgeist, aber du übertreibst nicht. Kein Therapie-Ton, keine langen Geschichten, keine Romane. Einfach warm, ruhig und normal."},

            {"role": "user", "content": frage}
        ],
        "temperature": 0.8,
        "max_tokens": 512
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        json_data = response.json()

        if "choices" not in json_data:
            return f"API Fehler: {json_data}"

        return json_data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"Fehler: {e}. Mondlicht hat Chaos erzeugt."

# ============================================================
# 🌙 Discord Bot Setup
# ============================================================

intents = discord.Intents.default()
intents.message_content = True  # WICHTIG für normale Nachrichten
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
# 🌙 Reaktion auf normale Nachrichten
# ============================================================

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.lower()

    # Trigger-Wörter
    trigger = ["liora", "lora", "mond", "geist"]

    if any(word in content for word in trigger):
        reply = call_liora(message.content)
        await message.channel.send(reply)

    # WICHTIG: Commands trotzdem verarbeiten
    await bot.process_commands(message)

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
