import os
import sys
from importlib import import_module
from importlib.util import find_spec
from pkgutil import walk_packages
from dotenv import load_dotenv
import discord
from discord.ext import commands

#CLASS IMPORT
sys.path.append('utils')
from GlobalString import GlobalString as GS
from Gestion import Gestion

#LOAD BOT TOKEN in .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

class GestionEmbed(commands.Bot, Gestion):
	
	async def on_ready(self):
		print("========================================================")
		print(bot.user.name, "has connected to Discord Bot API !")
		print("He's connected to", len(bot.guilds), "servers")
		print("========================================================")
		print("\nLogs : ")

	async def on_command_error(self, ctx, error):
		if isinstance(error, commands.errors.CheckFailure):
			await ctx.message.delete()
			new_msg = await ctx.send(GS.error_reinit)
			await new_msg.delete(delay=10)

#ALL TEMPLATES IMPORT FUNCTION
def import_templates(package, recursive=True):
	if isinstance(package, str):
		package = import_module(package)
	results = {}
	for loader, name, is_pkg in walk_packages(package.__path__):
		full_name = package.__name__ + '.' + name
		results[name] = import_module(full_name)
		if recursive and is_pkg:
			results.update(import_templates(full_name))
	return results


#MAIN
if __name__ == '__main__':
	#SEND TO DISCORD API WHAT I LOOK = Intents
	intents = discord.Intents(messages=True, guilds=True, members=True, presences=True, emojis=True, reactions=True)

	#LOAD GestionEmbed BOT
	bot = GestionEmbed(command_prefix='-', intents=intents)

	#IMPORT ALL TEMPLATES
	templates = {}
	tmp = import_templates("templates")
	for tem in tmp:
		try:
			templates[tem] = tmp[tem].get()
			bot.add_cog(templates[tem](bot))
			templates[tem] = bot.get_cog(tem)
		except(AttributeError):
			pass

	#ADD COMMAND GESTION
	bot.add_cog(Gestion(bot))
	Ges = bot.get_cog('Gestion')
	print(templates)
	Ges.set_templates(templates)

	#RUN BOT
	bot.run(TOKEN)