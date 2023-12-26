import os
import random
import discord
import discord.ext
from discord.ext import commands
import requests
import traceback

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.messages = True

bot = commands.Bot(command_prefix='/', intents=intents)

async def load_cogs():
  for f in os.listdir("./cogs"):
  	if f.endswith(".py"):
  		await bot.load_extension("cogs." + f[:-3])

async def unload_cogs():
  for f in os.listdir("./cogs"):
  	if f.endswith(".py"):
  		await bot.unload_extension("cogs." + f[:-3])

@bot.event # When the bot signs in:
async def on_ready():
  print("\n***---*** BoneyBot 1.0 Rebooting ***---***\n")
  print(f"Discord Username: {bot.user}\n")
  print("Loading all cogs from ./cogs:")
  await load_cogs()


my_secret = os.environ["DISCORD_LOGIN"] # Discord Login Details for Bot:
try:
  bot.run(my_secret)
except Exception as e:
  print("An error occurred: ", traceback.format_exc())
