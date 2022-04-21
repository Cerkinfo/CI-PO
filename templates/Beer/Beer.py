import discord, sys
from discord.ext import commands

import sys
sys.path.append('../../utils')
from GlobalString import GlobalString
from FunctionsForTemplates import FunctionsForTemplates

from .Livraison import Livraison
from .Branche import Branche
from .Vidange import Vidange

TEMPLATES_NAME = 'Beer'

def get():
	return Beer

async def good_templates(ctx):
		if type(ctx) is commands.Context:
			if ctx.channel.topic != None and ctx.channel.topic.split('\n')[0][len(GlobalString.gesTypeTopic):] == TEMPLATES_NAME:
				return True
		elif type(ctx) is discord.TextChannel:
			if ctx.topic != None and ctx.topic.split('\n')[0][len(GlobalString.gesTypeTopic):] == TEMPLATES_NAME:
				return True
		return False

class Beer(commands.Cog, FunctionsForTemplates, name=TEMPLATES_NAME):

	def __init__(self, bot):
		self.bot = bot
		self.name = TEMPLATES_NAME
		self.template = discord.Embed()
		self.livraison = Livraison()
		self.branche = Branche()
		self.vidange = Vidange()
		self.txt_action_emoji = [':truck:', ':beer:', ':repeat:']
		self.action_emoji = super().converter_text_to_emojis(self.txt_action_emoji)
		self.beer_status_embed = {'title':"𝙎𝙩𝙤𝙘𝙠 𝙙𝙪 𝙗𝙖𝙧", 'empty_stock':"Le stock est vide.", \
		'description':"", 'color':0xe8c259, 'footer': 'Livraison : ' + self.action_emoji[0] + '| Branchement : ' + self.action_emoji[1] + '| Vidange : ' + self.action_emoji[2], \
		'thumbnail':'http://assets.stickpng.com/images/595e5abd70308b1a215b70cf.png'}
		self.vidange_status_embed = {'title':"𝙎𝙩𝙤𝙘𝙠 𝙙𝙚 𝙫𝙞𝙙𝙖𝙣𝙜𝙚", 'empty_stock':"Aucune vidange.", \
		'description':"", 'color':0x8b17b5, 'footer':'', \
		'thumbnail':'http://bluebastard.ca/wp-content/uploads/2013/07/Half-full-pint-glass-beer.png'}

	async def startup(self, ctx):
		self.beer_status_embed['author'] = ctx.guild.name
		self.beer_status_embed['icon'] = str(ctx.guild.icon_url)
		self.vidange_status_embed['author'] = ctx.guild.name
		self.vidange_status_embed['icon'] = str(ctx.guild.icon_url)
		await ctx.channel.send("Index")
		await super().startup(self.vidange_status_embed)
		await ctx.channel.send(embed=self.template)
		await super().startup(self.beer_status_embed)
		#beer send in Gestion

	async def lock_channel(self, ctx):
		#other init
		await self.init_index(ctx.channel)
		beer_status_msg = await super().find_embed_with_title(ctx.channel, 2, self.beer_status_embed['title'])
		await super().react_to_msg(beer_status_msg, self.action_emoji)
		#permissions
		await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False, add_reactions=False, external_emojis=False)

##FEATURES
	async def is_beer_embed(self, msg):
		'''
		Vérifie si le message qui a reçu une réaction est bien le stock de bières.
		return : bool
		'''
		if len(msg.embeds) > 0:
			if msg.embeds[0].title == self.beer_status_embed['title']:
				return True

	async def beer_raw_reaction_add(self, chan, msg_react, emoji):
		if await self.is_beer_embed(msg_react):
			if emoji.name in self.action_emoji:
				if len(msg_react.reactions) > 2:
					await msg_react.clear_reactions()
					if emoji.name == self.action_emoji[0]:
						print('SERVEUR ' + chan.guild.name + ' IN CHANNEL ' + chan.name + ' RUN livraison')
						await self.livraison.init_livraison(chan)
					elif emoji.name == self.action_emoji[1]:
						print('SERVEUR ' + chan.guild.name + ' IN CHANNEL ' + chan.name + ' RUN branche')
						await self.branche.init_branche(chan)
					elif emoji.name == self.action_emoji[2]:
						print('SERVEUR ' + chan.guild.name + ' IN CHANNEL ' + chan.name + ' RUN vidange')
						await self.vidange.init_vidange(chan)

	async def init_index(self, channel):
		index_msg = await super().find_txt_msg(channel, 3, "Index")
		vidange_msg = await super().find_embed_with_title(channel, 2, self.vidange_status_embed['title'])
		beer_msg = await super().find_embed_with_title(channel, 2, self.beer_status_embed['title'])
		index = '\nStock Bar : '+str(beer_msg.id)+'\nStock Vidange : '+str(vidange_msg.id)
		await index_msg.edit(content=index)
		topic = '\nIndex of Embeds : '+str(index_msg.id)
		await channel.edit(topic=channel.topic+topic)

	async def get_embeds_storage(self, channel):
		topic = channel.topic
		topic = topic.split('\n')[1:]
		index_id = int(topic[0][len('Index of Embeds : '):])
		index_msg = await channel.fetch_message(index_id)
		index_msg = index_msg.content.split('\n')
		index_msg[0] = int(index_msg[0][len('Stock Bar : '):])
		index_msg[1] = int(index_msg[1][len('Stock Vidange : '):])
		beer_msg = await channel.fetch_message(index_msg[0])
		vidange_msg = await channel.fetch_message(index_msg[1])
		return [beer_msg, vidange_msg]

	async def update_embeds_id(self, channel, msgs=list):
		new_vidange_msg = await channel.send(embed=msgs[1].embeds[0])
		new_beer_msg = await channel.send(embed=msgs[0].embeds[0])
		topic = channel.topic
		topic = topic.split('\n')
		index_id = int(topic[1][len('Index of Embeds : '):])
		index_msg = await channel.fetch_message(index_id)
		index_cont = index_msg.content.split('\n')
		index_cont[0] = 'Stock Bar : ' + str(new_beer_msg.id)
		index_cont[1] = 'Stock Vidange : ' + str(new_vidange_msg.id)
		new_index = index_cont[0]+'\n'+index_cont[1]
		print(new_index)
		await index_msg.edit(content=new_index)
		await msgs[0].delete()
		await msgs[1].delete()
		await super().react_to_msg(new_beer_msg, self.action_emoji)
			
	async def set_history(self, history_msg):
		time = await super().set_timeFTT(history_msg.created_at)
		author = "History"
		title = None
		if history_msg.embeds[0].title == self.livraison.title or history_msg.embeds[0].title == self.livraison.title_confirm:
			footer = 'Date de réception le ' + time
			title = self.livraison.title_history
			description = ''
		elif history_msg.embeds[0].title == self.branche.title or history_msg.embeds[0].title == self.branche.title_confirm:
			footer = history_msg.embeds[0].footer.text.split('\n')[0] + '\n\nDate de branchement le ' + time
			title = self.branche.title_history
			description = None
		elif history_msg.embeds[0].title == self.vidange.title or history_msg.embeds[0].title == self.vidange.title_confirm:
			footer = 'Date de retour le ' + time
			title = self.vidange.title_history
			description = ''
		history_msg.embeds[0].set_footer(text=footer)
		history_msg.embeds[0].set_author(name=author)
		dict_ = history_msg.embeds[0].to_dict()
		dict_['title'] = title
		if description != None:
			dict_['description'] = description
		new_history_msg = discord.Embed.from_dict(dict_)
		await history_msg.edit(embed=new_history_msg)

	async def add_beers(self, channel, beers=dict, history=discord.Message):
		embed_msgs = await self.get_embeds_storage(channel)
		beer_setup_msg = embed_msgs[0]
		if self.beer_status_embed['empty_stock'] in beer_setup_msg.embeds[0].fields[0].name:
			beer_setup_msg.embeds[0].remove_field(0)
		print(beers)
		for name_beer in beers:
			if await super().find_field_in_embed_name(beer_setup_msg.embeds[0], name_beer):
				field, index = await super().find_field_in_embed_name(beer_setup_msg.embeds[0], name_beer)
				beer_setup_msg.embeds[0].set_field_at(index, name=field.name, value=int(field.value)+int(beers[name_beer]))
			else:
				beer_setup_msg.embeds[0].add_field(name=name_beer, value=beers[name_beer])
		await self.set_history(history)
		await self.update_embeds_id(channel, embed_msgs)

	async def remove_beer(self, channel, beer=list, history=discord.Message):
		embed_msgs = await self.get_embeds_storage(channel)
		beer_setup_msg = embed_msgs[0]
		history_msg = embed_msgs[1]
		avort = False
		if await super().find_field_in_embed_name(beer_setup_msg.embeds[0], beer[0]):
			field, index = await super().find_field_in_embed_name(beer_setup_msg.embeds[0], beer[0])
			beer_setup_msg.embeds[0].set_field_at(index, name=beer[0], value=str(int(field.value)-int(beer[1])))
			if int(beer_setup_msg.embeds[0].fields[index].value) < 0:
				avort = True
			if beer_setup_msg.embeds[0].fields[index].value == '0':
				beer_setup_msg.embeds[0].remove_field(index)
		await super().empty_stock(beer_setup_msg.embeds[0], self.beer_status_embed['empty_stock'])
		print(beer)
		if self.vidange_status_embed['empty_stock'] in history_msg.embeds[0].fields[0].name:
			history_msg.embeds[0].remove_field(0)
		if await super().find_field_in_embed_name(history_msg.embeds[0], beer[0]):
			field, index = await super().find_field_in_embed_name(history_msg.embeds[0], beer[0])
			history_msg.embeds[0].set_field_at(index, name=field.name, value=str(int(field.value)+int(beer[1])))
		else:
			history_msg.embeds[0].add_field(name=beer[0], value=beer[1])
		if avort:
			await history.delete()
			await channel.send(":warning: L'une des bières que vous souhaitez brancher n'est plus en quantité suffisante par rapport à la quantité demandée.\
				\n:x: **Opération annulée, veuillez recommencer ou mettre à jour votre stock**", delete_after=10)
			await super().react_to_msg(beer_setup_msg, self.action_emoji)
		else:
			await self.set_history(history)
			await self.update_embeds_id(channel, embed_msgs)

	async def remove_vidanges(self, channel, vidanges=dict, history=discord.Message):
		embed_msgs = await self.get_embeds_storage(channel)
		history_msg = embed_msgs[1]
		avort = False
		print(vidanges)
		for name_vids in vidanges:
			if await super().find_field_in_embed_name(history_msg.embeds[0], name_vids):
				field, index = await super().find_field_in_embed_name(history_msg.embeds[0], name_vids)
				history_msg.embeds[0].set_field_at(index, name=field.name, value=str(int(field.value)-int(vidanges[name_vids])))
				if int(history_msg.embeds[0].fields[index].value) < 0:
					avort = True
				if history_msg.embeds[0].fields[index].value == '0':
					history_msg.embeds[0].remove_field(index)
		if avort:
			await history.delete()
			await channel.send(":warning: L'une des vidanges que vous souhaitez rendre n'est plus en quantité suffisante par rapport à la quantité demandée.\
				\n:x: **Opération annulée, veuillez recommencer ou mettre à jour votre stock**", delete_after=10)
			await super().react_to_msg(embed_msgs[0], self.action_emoji)
		else:
			await super().empty_stock(history_msg.embeds[0], self.vidange_status_embed['empty_stock'])
			await self.set_history(history)
			await self.update_embeds_id(channel, embed_msgs)


	async def get_beers(self, channel):
		embed_msgs = await self.get_embeds_storage(channel)
		beer_setup_msg = embed_msgs[0]
		if self.beer_status_embed['empty_stock'] in beer_setup_msg.embeds[0].fields[0].name:
			return None
		beers = []
		for field in beer_setup_msg.embeds[0].fields:
			beers.append(field.name.split(' - '))
		return beers

	async def get_vidanges(self, channel):
		embed_msgs = await self.get_embeds_storage(channel)
		history_msg = embed_msgs[1]
		if self.vidange_status_embed['empty_stock'] in history_msg.embeds[0].fields[0].name:
			return None
		vidanges = []
		for field in history_msg.embeds[0].fields:
			vidanges.append((field.name.split(' - ')[0], field.name.split(' - ')[1]))
		return vidanges

##EVENTS

	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload):
		if not payload.member.bot:
			message = await super().get_message_got_reaction(payload)
			channel = message.channel
			if await good_templates(channel):
				await self.beer_raw_reaction_add(channel, message, payload.emoji)
				await self.livraison.livraison_raw_reaction_add(channel, message, payload.emoji)
				await self.branche.branche_raw_reaction_add(channel, message, payload.emoji)
				await self.vidange.vidange_raw_reaction_add(channel, message, payload.emoji)

	@commands.Cog.listener()
	async def on_message(self, message):
		if not message.author.bot:
			if await good_templates(message.channel):
				await self.livraison.to_livraison_send_message(message)
				await self.branche.to_branche_send_message(message)
				await self.vidange.to_vidange_send_message(message)
##COMMANDS

	@commands.command(name='livraison')
	@commands.check(good_templates)
	async def livraison(self, ctx):
		print('livraison')
		await ctx.message.delete()
		await self.livraison.init_livraison(ctx.message.channel)
	
	@commands.command(name='branche')
	@commands.check(good_templates)
	async def branche(self, ctx):
		print('branche')
		await ctx.message.delete()
		await self.branche.init_branche(ctx.message.channel)

	@commands.command(name='vidange')
	@commands.check(good_templates)
	async def vidange(self, ctx):
		print('vidange')
		await ctx.message.delete()
		await self.vidange.init_vidange(ctx.message.channel)