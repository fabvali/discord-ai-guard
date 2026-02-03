from dotenv import load_dotenv
import os
import re
import json
import discord
import aiohttp
from discord.ext import commands
from discord import app_commands
from pathlib import Path

load_dotenv(dotenv_path=".env")
token = os.getenv("DISCORD_TOKEN")
chutes_url = os.getenv("CHUTES_BASE_URL")
model = os.getenv("CHUTES_MODEL")
api_key = os.getenv("CHUTES_API_KEY")

data_file = Path("automod_guilds.json")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True


def load_guilds():
    if not data_file.exists():
        return {}
    try:
        with open(data_file, "r") as f:
            raw = json.load(f)
            return {int(k): v for k, v in raw.items()}
    except:
        return {}


def save_guilds(data):
    with open(data_file, "w") as f:
        json.dump(data, f)


class AutoModBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents, help_command=None)
        self.session = None
        self.enabled_guilds = load_guilds()

    async def setup_hook(self):
        self.session = aiohttp.ClientSession()
        await self.tree.sync()

    async def close(self):
        if self.session:
            await self.session.close()
        save_guilds(self.enabled_guilds)
        await super().close()

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        await self.change_presence(activity=discord.Game(name="AI AutoMod"))

    async def check_message(self, text):
        if not self.session or not api_key:
            return None, None

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": text}],
            "stream": True,
        }

        try:
            async with self.session.post(f"{chutes_url}/chat/completions", headers=headers, json=payload, timeout=20) as resp:
                if resp.status != 200:
                    print(f"Chutes error: {resp.status}")
                    return None, None

                chunks = []
                async for chunk in resp.content:
                    if not chunk:
                        continue
                    
                    decoded = chunk.decode("utf-8")
                    
                    try:
                        data = json.loads(decoded)
                    except:
                        s = decoded.strip()
                        if s.startswith("data:"):
                            s = s[5:].strip()
                        if not s:
                            continue
                        try:
                            data = json.loads(s)
                        except:
                            continue

                    if not data.get("choices"):
                        continue
                        
                    delta = data["choices"][0].get("delta", {})
                    content = delta.get("content")
                    if content:
                        chunks.append(content)

        except Exception as e:
            print(f"Request failed: {e}")
            return None, None

        full_text = "".join(chunks).strip()
        
        print("Qwen3Guard response:")
        print(repr(full_text))
        print("----")

        safety_match = re.search(r"Safety:\s*(Safe|Unsafe|Controversial)", full_text, re.IGNORECASE)
        cat_match = re.search(r"Categories:\s*(.*)", full_text, re.IGNORECASE)

        safety = safety_match.group(1).capitalize() if safety_match else None
        categories = cat_match.group(1).strip() if cat_match else None

        return safety, categories

    async def on_message(self, message):
        guild_name = message.guild.name if message.guild else "DM"
        channel_name = message.channel.name if hasattr(message.channel, "name") else "DM"
        print(f"[MSG] {guild_name} #{channel_name} <{message.author}>: {message.content}")

        if message.author.bot:
            await self.process_commands(message)
            return

        safety, categories = await self.check_message(message.content)
        print(f"[GUARD] safety={safety}, categories={categories}")

        if message.guild and self.enabled_guilds.get(message.guild.id) and safety:
            if safety == "Controversial":
                ### Adds a reaction if something controversal is detected but not deleted (often annoying) ###
                #try:
                #    await message.add_reaction("👀")
                #except discord.HTTPException:
                #    pass
                print("CONTROVERSIAL")

            elif safety == "Unsafe":
                try:
                    await message.delete()
                except:
                    pass

                try:
                    await message.channel.send(
                        f"{message.author.mention} your message was removed. Reason: `{categories}`."
                    )
                except:
                    pass

        await self.process_commands(message)


bot = AutoModBot()


@bot.tree.command(name="automod", description="Enable or disable AI automod for this server.")
@app_commands.describe(enabled="True to enable, False to disable")
async def automod(interaction: discord.Interaction, enabled: bool):
    app_info = await bot.application_info()
    if interaction.user.id != app_info.owner.id:
        await interaction.response.send_message("Only the bot owner can use this command.", ephemeral=True)
        return
    
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return

    bot.enabled_guilds[interaction.guild.id] = enabled
    save_guilds(bot.enabled_guilds)
    state = "enabled" if enabled else "disabled"
    await interaction.response.send_message(f"AI automod has been **{state}** for this server.", ephemeral=True)


if __name__ == "__main__":
    bot.run(token)
