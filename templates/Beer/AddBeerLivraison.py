import discord
from discord.ext import commands

import sys
sys.path.append('../../utils')
from GlobalString import GlobalString
from FunctionsForTemplates import FunctionsForTemplates

class AddBeerLivraison(FunctionsForTemplates):
	def __init__(self):
		self.add_beer_fields = ('Autres', 'Boissons')
		self.txt_new_beer_emoji = ':new:'
		self.new_beer_emoji = super().converter_text_to_emojis(self.txt_new_beer_emoji)[0]
		self.ctrl_add_emoji = super().converter_text_to_emojis([':arrow_forward:',':stop_button:'])
		self.title='Ajouter une bière livrée'
		self.author="Add Beer Livraison Setup"
		self.description="Ajoutez autant de boissons que vous souhaitez en répondant correctement"
		self.color=0x16e339
		self.footer = 'Cliquez sur ' + self.ctrl_add_emoji[0] + ' pour ajouter une autre boisson. Ou ' + self.ctrl_add_emoji[1] + 'pour arrêter les ajouts.'
		self.footer = super().converter_text_to_emojis(self.footer)[0]
		self.begin_of_txt_ask_msg = '***Add Beer Livraison Setup*** : '
		self.add_beer_livraison_embed = {'title':self.title, 'empty_stock':"L'ajout est vide.", 'author':self.author, \
		'icon':'?', 'description':self.description, 'color':self.color, 'footer':self.footer, 'thumbnail':''}
		
	async def is_add_beer_livraison_embed(self, msg):
		'''
		Vérifie si le message qui a reçu une réaction est bien le setup de livraison.
		return : bool
		'''
		if len(msg.embeds) > 0:
			if msg.embeds[0].title == self.title:
				return True

	async def add_beer_livraison_raw_reaction_add(self, chan, msg_react, emoji):
		'''
		La moitié de l'enchainement des "évenements" se passe ici. Lorsuqu'une réaction à un emoji est requise. 
		Si elle se produit, cette fonction trie puis déclenche le bon scénario
		return : void
		'''
		if await self.is_add_beer_livraison_embed(msg_react):
			if emoji.name == self.ctrl_add_emoji[1]:
			#stop
				from .Livraison import Livraison
				await Livraison().add_new_beer_to_fields(msg_react)
			elif emoji.name == self.ctrl_add_emoji[0]:
			#continue add
				await msg_react.clear_reactions()
				await self.ask_new_beer(msg_react, 0)

	async def to_add_beer_livraison_send_message(self, message):
		add_beer_livraison_setup_id = await super().find_id_in_msg(message.channel, GlobalString.id_identificator)
		add_beer_livraison_setup_msg = await message.channel.fetch_message(int(add_beer_livraison_setup_id))
		await self.add_beer_to_fields(add_beer_livraison_setup_msg, message)

	async def init_add_beer_livraison(self, channel):
		self.template = discord.Embed()
		await super().startup(self.add_beer_livraison_embed)
		add_beer_livraison_setup_msg = await channel.send(embed=self.template)
		await self.ask_new_beer(add_beer_livraison_setup_msg, 0)

	async def ask_new_beer(self, add_beer_livraison_setup_msg, question=int):
		id = '||'+GlobalString.id_identificator+str(add_beer_livraison_setup_msg.id)+'||\n'
		if question == 0:
			msg = "Quel est le nom de la bière que vous avez acheté ?"
		elif question == 1:
			msg = "Quelle est la capacité en LITRES du contenant ? (utilisez le point et non la virgule si celle-ci est nécessaire)"
		await add_beer_livraison_setup_msg.channel.send(id+self.begin_of_txt_ask_msg+msg)

	async def add_beer_to_fields(self, add_beer_livraison_setup_msg, message):
		try:
			litre = float(message.content)
			index = len(add_beer_livraison_setup_msg.embeds[0].fields)-1
			add_beer_livraison_setup_msg.embeds[0].set_field_at(index, name=add_beer_livraison_setup_msg.embeds[0].fields[index].name+' '+message.content+'L', value=0)
			await add_beer_livraison_setup_msg.edit(embed=add_beer_livraison_setup_msg.embeds[0])
			await super().cleanup(message.channel, add_beer_livraison_setup_msg.id)
			await super().react_to_msg(add_beer_livraison_setup_msg, self.ctrl_add_emoji)
		except(ValueError):
			if add_beer_livraison_setup_msg.embeds[0].fields[0].name == self.add_beer_livraison_embed['empty_stock']:
				add_beer_livraison_setup_msg.embeds[0].remove_field(0)
			name = message.content
			add_beer_livraison_setup_msg.embeds[0].add_field(name=':new: : '+message.content+' -', value=0)
			await add_beer_livraison_setup_msg.edit(embed=add_beer_livraison_setup_msg.embeds[0])
			await self.ask_new_beer(add_beer_livraison_setup_msg, 1)