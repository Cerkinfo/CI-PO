from discord.ext import commands

import sys
sys.path.append('utils')
from GlobalString import GlobalString as GS
from FunctionsForTemplates import FunctionsForTemplates

class Gestion(commands.Cog, name='Gestion'):

	def set_templates(self, temp):
		self.templates = temp

	@commands.command(name="discord")
	async def g_exist(self, ctx):
		print("scord")
		await ctx.send("scord")

	@commands.command(name="gestion", help=GS.help_gestion)
	@commands.check(FunctionsForTemplates().not_active)
	async def init_embed(self, ctx, gesType):
		print("init gestion channel as "+gesType)
		obj = self.templates[gesType]
		await ctx.channel.edit(topic=GS.gesTypeTopic+gesType)
		await obj.startup(ctx)
		await ctx.send(embed=obj.template)
		await ctx.message.delete()
		await obj.lock_channel(ctx)