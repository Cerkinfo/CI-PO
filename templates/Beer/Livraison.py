import discord
from discord.ext import commands

import sys
sys.path.append('../../utils')
from EmojisList import *
from GlobalString import GlobalString
from FunctionsForTemplates import FunctionsForTemplates
from .AddBeerLivraison import AddBeerLivraison

class Livraison(FunctionsForTemplates):
	def __init__(self):
		self.add_beer_livraison = AddBeerLivraison()
		self.ctrl_emojis = super().converter_text_to_emojis(txt_ctrl_emojis)
		self.beers = [('Jupiler', '50L'), ('Kasteel Red', '0.35L'), ('Triple Karmeliet', '0.25L'), ('Kriek', '0.25L'), ('Ice-Tea', '1L')]
		self.title='Menu des Bières les + Populaires'
		self.title_confirm='Confirmez-vous cette livraison ?'
		self.title_history='Détail de la livraison reçu'
		self.author="Livraison Setup"
		self.description="Choisissez les bières livrés en cliquant sur l'Emoji correspondant"
		self.color=0x16e339
		self.footer = 'Cliquez sur ' + txt_ctrl_emojis[0] + ' pour valider. Ou ' + txt_ctrl_emojis[1] + ' pour annuler.'
		self.footer = super().converter_text_to_emojis(self.footer)[0]
		self.begin_of_txt_ask_msg = '***Livraison Setup*** : '
		self.livraison_embed = {'title':self.title, 'empty_stock':"Le stock est vide.", 'author':self.author, \
		'icon':'?', 'description':self.description, 'color':self.color, 'footer':self.footer, 'thumbnail':''}
		
	async def is_livraison_embed(self, msg):
		'''
		Vérifie si le message qui a reçu une réaction est bien le setup de livraison.
		return : bool
		'''
		if len(msg.embeds) > 0:
			if msg.embeds[0].title == self.title or msg.embeds[0].title == self.title_confirm:
				return True

	async def livraison_raw_reaction_add(self, chan, msg_react, emoji):
		'''
		La moitié de l'enchainement des "évenements" se passe ici. Lorsuqu'une réaction à un emoji est requise. 
		Si elle se produit, cette fonction trie puis déclenche le bon scénario
		return : void
		'''
		if await self.is_livraison_embed(msg_react):
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
						#start livraison or in progress
						cancel = True
						new = False
						for react in msg_react.reactions:
							if react.count > 1 and react.emoji not in self.ctrl_emojis:
								cancel = False
							if react.count > 1 and react.emoji == self.add_beer_livraison.new_beer_emoji:
								new = True
						if cancel:
							await self.avort_message(msg_react)
							st_embeds = await b.get_embeds_storage(chan)
							await super().react_to_msg(st_embeds[0], b.action_emoji)
						else:
							await self.valid_livraison(msg_react)
							if new:
								await self.add_beer_livraison.init_add_beer_livraison(chan)
							else:
								next_beer = await self.get_beer_to_ask(msg_react)
								await self.ask_qt(chan, next_beer, msg_react.id)
					else:
						#confirm final livraison and stop it
						to_add = {}
						for field in msg_react.embeds[0].fields:
							for emo in txt_random_emojis+[self.add_beer_livraison.txt_new_beer_emoji]:
								if emo in field.name: to_add[field.name[len(emo)+3:]] = field.value
						await msg_react.clear_reactions()
						await b.add_beers(chan, to_add, msg_react)
		elif await self.add_beer_livraison.is_add_beer_livraison_embed(msg_react):
			await self.add_beer_livraison.add_beer_livraison_raw_reaction_add(chan, msg_react, emoji)

	async def to_livraison_send_message(self, message):
		'''
		L'autre moitié du scénario se passe ici, si une réponse manuscrite est requise, elle est vérifiée,
		traitée et envoyée aux bonnes fonctions. Provoque une erreur si contextuelle.
		return : void
		'''
		if await super().find_txt_msg(message.channel, 3, self.begin_of_txt_ask_msg):
		#found an answer to the quantity of beer received 
			try:
				beer_qt = int(message.content)
				1/beer_qt #if beer_qt = 0 -> ZeroDivisionError
				livraison_setup_id = await super().find_id_in_msg(message.channel, GlobalString.id_identificator)
				livraison_setup_msg = await message.channel.fetch_message(livraison_setup_id)
				beer_for_qt = await self.get_beer_asked(message)
				await self.add_qt_value_to_field(livraison_setup_msg, beer_qt, beer_for_qt)
				#loop for ask next beer on selection, otherwise run finish setup
				next_beer = await self.get_beer_to_ask(livraison_setup_msg, beer_for_qt)
				await self.ask_qt(message.channel, next_beer, livraison_setup_msg.id)
			except(ValueError, ZeroDivisionError):
				beer_for_qt = await self.get_beer_asked(message)
				livraison_setup_id = await super().find_id_in_msg(message.channel, GlobalString.id_identificator)
				await message.channel.send("Je n'ai pas compris votre réponse. Veuillez n'entrer qu'un nombre supérieur à zéro svp, rien d'autre.")
				await self.ask_qt(message.channel, beer_for_qt, livraison_setup_id)
		if await super().find_txt_msg(message.channel, 3, self.add_beer_livraison.begin_of_txt_ask_msg):
			await self.add_beer_livraison.to_add_beer_livraison_send_message(message)

	async def init_livraison(self, channel):
		self.template = discord.Embed()
		await super().startup(self.livraison_embed)
		self.template.remove_field(0) #empty stock
		txt_list_emo = await super().get_random_emojis(len(self.beers), txt_random_emojis)
		list_emo = super().converter_text_to_emojis(txt_list_emo)
		for i in range(len(self.beers)):
			self.template.add_field(name=txt_list_emo[i]+' : '+self.beers[i][0]+' - '+self.beers[i][1], value=0)
		self.template.add_field(name=self.add_beer_livraison.txt_new_beer_emoji+' : '+self.add_beer_livraison.add_beer_fields[0]+' - '+self.add_beer_livraison.add_beer_fields[1], value=0)
		livraison_setup_msg = await channel.send(embed=self.template)
		await super().react_to_msg(livraison_setup_msg, list_emo+[self.add_beer_livraison.new_beer_emoji]+self.ctrl_emojis)

	async def valid_livraison(self, livraison_setup_msg):
		list_react = livraison_setup_msg.reactions
		fields = livraison_setup_msg.embeds[0].fields
		to_remove = list()
		for react in list_react:
			if react.emoji not in self.ctrl_emojis and react.count == 1:
				to_remove.append(fields[list_react.index(react)])
		while(len(to_remove) > 0):
			livraison_setup_msg.embeds[0].remove_field(fields.index(to_remove[0]))
			fields.pop(fields.index(to_remove[0]))
			to_remove.pop(0)
		await super().unlock_writing(livraison_setup_msg.channel, 1, livraison_setup_msg)
		await livraison_setup_msg.clear_reactions()
		await livraison_setup_msg.edit(embed=livraison_setup_msg.embeds[0])

	async def end_livraison(self, livraison_setup_msg):
		await super().lock_writing(livraison_setup_msg.channel, 1, await super().who_writing(livraison_setup_msg.channel, 1))
		await super().cleanup(livraison_setup_msg.channel, livraison_setup_msg.id)
		dict_livraison = livraison_setup_msg.embeds[0].to_dict()
		dict_livraison['title'] = self.title_confirm
		new_livraison_setup_msg = discord.Embed.from_dict(dict_livraison)
		await livraison_setup_msg.edit(embed=new_livraison_setup_msg)
		await super().react_to_msg(livraison_setup_msg, self.ctrl_emojis)

	async def get_beer_asked(self, msg_qt):
		ask_msg = await super().find_txt_msg(msg_qt.channel, 2, self.begin_of_txt_ask_msg)
		livraison_setup_id = await super().find_id_in_msg(msg_qt.channel, GlobalString.id_identificator)
		livraison_setup_msg = await ask_msg.channel.fetch_message(int(livraison_setup_id))
		beer_and_qt = ask_msg.content.split('**`')[1].split('`**')[0].split(' ')
		for field in livraison_setup_msg.embeds[0].fields:
			inside = True
			for part in beer_and_qt:
				if part not in field.name:
					inside = False
			if inside == True:
				ret = ''
				for i in range(len(beer_and_qt)-1):
					if ret != '':
						ret = ret + ' '
					ret = ret + beer_and_qt[i]
				return (ret, beer_and_qt[len(beer_and_qt)-1])

	async def find_index_field_to_beer(self, field):
		for emo in txt_random_emojis+[self.add_beer_livraison.txt_new_beer_emoji]:
			if emo in field.name and field.value == '0':
				return (field.name.split(' - ')[0][len(emo+' : '):],field.name.split(' - ')[1])
				
	async def get_beer_to_ask(self, livraison_setup_msg, previous_beer=None):
		if previous_beer != None:
			previous_field, index = await super().find_field_in_embed_name(livraison_setup_msg.embeds[0], previous_beer)
			if len(livraison_setup_msg.embeds[0].fields) > index+1:
				next_field = livraison_setup_msg.embeds[0].fields[index+1]
				return await self.find_index_field_to_beer(next_field)
		else:
			for field in livraison_setup_msg.embeds[0].fields:
				try_ = await self.find_index_field_to_beer(field)
				if try_ != None:
					return try_
				
	async def ask_qt(self, channel, beer, lsmsg_id):
		if beer != None:
			id = '||'+GlobalString.id_identificator+str(lsmsg_id)+'||\n'
			msg = "Quelle quantité de **`" + beer[0] + " " + beer[1] + "`** a été livrée ?"
			await channel.send(id+self.begin_of_txt_ask_msg+msg)
		else:
			await self.end_livraison(await channel.fetch_message(lsmsg_id))
			
	async def add_qt_value_to_field(self, livraison_setup_msg, message_qt, linked_beer):
		target_field, index_field = await super().find_field_in_embed_name(livraison_setup_msg.embeds[0], linked_beer)
		livraison_setup_msg.embeds[0].set_field_at(index_field, name=target_field.name, value=message_qt)
		await livraison_setup_msg.edit(embed=livraison_setup_msg.embeds[0])

	async def add_new_beer_to_fields(self, add_beer_livraison_setup_msg):
		livraison_setup_msg = await super().find_embed_with_title(add_beer_livraison_setup_msg.channel, 2, self.title)
		livraison_setup_msg.embeds[0].remove_field(len(livraison_setup_msg.embeds[0].fields)-1)
		for field in add_beer_livraison_setup_msg.embeds[0].fields:
			stop = False
			for f in livraison_setup_msg.embeds[0].fields:
				if field.name[len(self.add_beer_livraison.txt_new_beer_emoji+' : '):] in f.name:
					stop = True
			if not stop:
				livraison_setup_msg.embeds[0].add_field(name=field.name, value=0)
		await livraison_setup_msg.edit(embed=livraison_setup_msg.embeds[0])
		await super().avort_message(add_beer_livraison_setup_msg)
		next_beer = await self.get_beer_to_ask(livraison_setup_msg)
		await self.ask_qt(livraison_setup_msg.channel, next_beer, livraison_setup_msg.id)
