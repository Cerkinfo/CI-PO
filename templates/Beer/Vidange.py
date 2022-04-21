import discord
from discord.ext import commands

import sys
sys.path.append('../../utils')
from EmojisList import *
from FunctionsForTemplates import FunctionsForTemplates
from GlobalString import GlobalString

class Vidange(FunctionsForTemplates):
	def __init__(self):
		self.ctrl_emojis = super().converter_text_to_emojis(txt_ctrl_emojis)
		self.title='Menu des Vidanges dans votre Stock'
		self.title_confirm='Confirmez-vous ce retour ?'
		self.title_history='Détail du retour de vidanges'
		self.author="Vidange Setup"
		self.description="Choisissez les vidanges rendus en cliquant sur l'Emoji correspondant"
		self.color=0xdd0e0e
		self.footer = "Cliquez sur " +txt_ctrl_emojis[0]+ " pour valider. Ou " +txt_ctrl_emojis[1]+ " pour annuler."
		self.footer = super().converter_text_to_emojis(self.footer)[0]
		self.begin_of_txt_ask_msg = '***Vidange Setup*** : '
		self.vidange_embed = {'title':self.title, 'empty_stock':"Le stock est vide.", 'author':self.author, \
		'icon':'?', 'description':self.description, 'color':self.color, 'footer':self.footer, 'thumbnail':''}

	async def is_vidange_embed(self, msg):
		'''
		Vérifie si le message qui a reçu une réaction est bien le setup de vidange.
		return : bool
		'''
		if len(msg.embeds) > 0:
			if msg.embeds[0].title == self.title or msg.embeds[0].title == self.title_confirm:
				return True

	async def vidange_raw_reaction_add(self, chan, msg_react, emoji):
		'''
		return : void
		'''
		if await self.is_vidange_embed(msg_react):
			if emoji.name in self.ctrl_emojis:
				from .Beer import Beer
				b = Beer(None)
				if emoji.name == self.ctrl_emojis[1]:
				#cancelation
					await self.avort_message(msg_react)
					st_embeds = await b.get_embeds_storage(chan)
					await super().react_to_msg(st_embeds[0], b.action_emoji)
				elif emoji.name == self.ctrl_emojis[0]:
				#validation
					if len(msg_react.reactions) > 2:
						#start vidange
						cancel = True
						for react in msg_react.reactions:
							if react.count > 1 and react.emoji not in self.ctrl_emojis:
								cancel = False
						if cancel:
							await self.avort_message(msg_react)
							st_embeds = await b.get_embeds_storage(chan)
							await super().react_to_msg(st_embeds[0], b.action_emoji)
						else:
							await self.valid_vidange(msg_react)
						next_beer = await self.get_beer_to_ask(msg_react)
						await self.ask_qt(chan, next_beer, msg_react.id)
					else:
						#confirm final vidange and stop it
						to_remove = {}
						for field in msg_react.embeds[0].fields:
							for emo in txt_random_emojis:
								if emo in field.name: to_remove[field.name[len(emo)+3:]] = field.value
						await msg_react.clear_reactions()
						await b.remove_vidanges(chan, to_remove, msg_react)

	async def to_vidange_send_message(self, message):
		if await super().find_txt_msg(message.channel, 3, self.begin_of_txt_ask_msg):
		#found an answer to the quantity of vidange gived
			try:
				vidange_qt = int(message.content)
				1/vidange_qt #if vidange_qt = 0 -> ZeroDivisionError
				vidange_setup_id = await super().find_id_in_msg(message.channel, GlobalString.id_identificator)
				vidange_setup_msg = await message.channel.fetch_message(vidange_setup_id)
				vidange_for_qt = await self.get_beer_asked(message)
				await self.add_qt_value_to_field(vidange_setup_msg, vidange_qt, vidange_for_qt)
				#loop for ask next beer on selection, otherwise run finish setup
				next_beer = await self.get_beer_to_ask(vidange_setup_msg, vidange_for_qt)
				await self.ask_qt(message.channel, next_beer, vidange_setup_msg.id)
			except(ValueError, ZeroDivisionError):
				vidange_for_qt = await self.get_beer_asked(message)
				vidange_setup_id = await super().find_id_in_msg(message.channel, GlobalString.id_identificator)
				await message.channel.send("Je n'ai pas compris votre réponse. Veuillez n'entrer qu'un nombre supérieur à zéro svp, rien d'autre.")
				await self.ask_qt(message.channel, vidange_for_qt, vidange_setup_id)


	async def init_vidange(self, channel):
		from .Beer import Beer
		self.template = discord.Embed()
		await super().startup(self.vidange_embed)
		self.template.remove_field(0) #empty_stock
		Beer_obj = Beer(None)
		beer_stock = await super().find_embed_with_title(channel, 5, Beer_obj.beer_status_embed['title'])
		vidanges = await Beer_obj.get_vidanges(channel)
		if vidanges == None:
			await channel.send(":warning: Le stock de vidange est vide.\n:x: **Opération annulée**", delete_after=7)
			await super().react_to_msg(beer_stock, Beer_obj.action_emoji)
		else:
			txt_list_emo = await super().get_random_emojis(len(vidanges), txt_random_emojis)
			list_emo = super().converter_text_to_emojis(txt_list_emo)
			for i in range(len(vidanges)):
				self.template.add_field(name=txt_list_emo[i]+' : '+vidanges[i][0]+' - '+vidanges[i][1], value=0)
			vidange_setup_msg = await channel.send(embed=self.template)
			await super().react_to_msg(vidange_setup_msg, list_emo+self.ctrl_emojis)

	async def valid_vidange(self, vidange_setup_msg):
		list_react = vidange_setup_msg.reactions
		fields = vidange_setup_msg.embeds[0].fields
		to_remove = list()
		for react in list_react:
			if react.emoji not in self.ctrl_emojis and react.count == 1:
				to_remove.append(fields[list_react.index(react)])
		while(len(to_remove) > 0):
			vidange_setup_msg.embeds[0].remove_field(fields.index(to_remove[0]))
			fields.pop(fields.index(to_remove[0]))
			to_remove.pop(0)
		dict_vidange = vidange_setup_msg.embeds[0].to_dict()
		dict_vidange['title'] = self.title_confirm
		new_vidange_setup_msg = discord.Embed.from_dict(dict_vidange)
		await super().unlock_writing(vidange_setup_msg.channel, 1, vidange_setup_msg)
		await vidange_setup_msg.clear_reactions()
		await vidange_setup_msg.edit(embed=new_vidange_setup_msg)

	async def end_vidange(self, vidange_setup_msg):
		await super().lock_writing(vidange_setup_msg.channel, 1, await super().who_writing(vidange_setup_msg.channel, 1))
		await super().cleanup(vidange_setup_msg.channel, vidange_setup_msg.id)
		await super().react_to_msg(vidange_setup_msg, self.ctrl_emojis)

	async def get_beer_asked(self, msg_qt):
		from .Beer import Beer
		vidanges = await Beer(None).get_vidanges(msg_qt.channel)
		ask_msg = await super().find_txt_msg(msg_qt.channel, 2, self.begin_of_txt_ask_msg)
		for vid in vidanges:
			if vid[0] in ask_msg.content and vid[1] in ask_msg.content:
				return vid

	async def find_index_field_to_beer(self, field):
		for emo in txt_random_emojis:
			if emo in field.name and field.value == '0':
					return (field.name.split(' - ')[0].split(' : ')[1], field.name.split(' - ')[1])

	async def get_beer_to_ask(self, vidange_setup_msg, previous_beer=None):
		if previous_beer != None:
			previous_field, index = await super().find_field_in_embed_name(vidange_setup_msg.embeds[0], previous_beer)
			if len(vidange_setup_msg.embeds[0].fields) > index+1:
				next_field = vidange_setup_msg.embeds[0].fields[index+1]
				return await self.find_index_field_to_beer(next_field)
		else:
			for field in vidange_setup_msg.embeds[0].fields:
				try_ = await self.find_index_field_to_beer(field)
				if try_ != None:
					return try_
				
	async def ask_qt(self, channel, beer, vidange_setup_id):
		if beer != None:
			id = '||'+GlobalString.id_identificator+str(vidange_setup_id)+'||\n'
			msg = "Quelle quantité de **`" + beer[0] + " " + beer[1] + "`** a été rendu ?"
			await channel.send(id+self.begin_of_txt_ask_msg+msg)
		else:
			await self.end_vidange(await channel.fetch_message(vidange_setup_id))
			
	async def add_qt_value_to_field(self, vidange_setup_msg, message_qt, linked_beer):
		target_field, index_field = await super().find_field_in_embed_name(vidange_setup_msg.embeds[0], linked_beer)
		vidange_setup_msg.embeds[0].set_field_at(index_field, name=target_field.name, value=message_qt)
		await vidange_setup_msg.edit(embed=vidange_setup_msg.embeds[0])
