import discord
from discord.ext import commands

import sys
sys.path.append('../../utils')
from EmojisList import *
from FunctionsForTemplates import FunctionsForTemplates
from GlobalString import GlobalString

class Branche(FunctionsForTemplates):
	def __init__(self):
		self.txt_bran_ctrl_emojis = [':white_check_mark:',':pencil:',':x:']
		self.bran_ctrl_emojis = super().converter_text_to_emojis(self.txt_bran_ctrl_emojis)
		self.txt_payement_emojis = [':euro:', ':stop_sign:']
		self.payement_emojis = super().converter_text_to_emojis(self.txt_payement_emojis)
		self.ctrl_emojis = super().converter_text_to_emojis(txt_ctrl_emojis)
		self.title='Quelle Bière de votre Stock branchez-vous?'
		self.title_confirm = 'Confirmez-vous ces paramètres de branchement ?'
		self.title_history = 'Détail du branchement réalisé'
		self.author="Branchement Setup"
		self.description="Choisissez UNE bière percée en cliquant sur l'Emoji correspondant"
		self.color=0x0E99F5
		self.footer = "Cliquez sur " +self.txt_bran_ctrl_emojis[0]+ " pour valider. Ou " +self.txt_bran_ctrl_emojis[2]+ " pour annuler."
		self.footer = super().converter_text_to_emojis(self.footer)[0]
		self.footer_wPencil = 'Valider : '+self.bran_ctrl_emojis[0]+' Modifier : '+self.bran_ctrl_emojis[1]+' Annuler : '+self.bran_ctrl_emojis[2]
		self.begin_of_txt_ask_msg = '***Branchement Setup*** : '
		self.branche_embed = {'title':self.title, 'empty_stock':"Le stock est vide.", 'author':self.author, \
		'icon':'?', 'description':self.description, 'color':self.color, 'footer':self.footer, 'thumbnail':''}
		self.modify_questions = [("Qui est l'acheteur ?", "Le Bar", str), ("Quelle est la raison de ce branchement ?", "Pré-TD", str), \
			("Qui a autorisé le branchement ?", "X", str), ("Quelle quantité avez-vous branché ?", "1", int), ("Quel est le mode paiement ?", "En cash", str)]
		
	async def is_branche_embed(self, msg):
		'''
		Vérifie si le message qui a reçu une réaction est bien le setup de livraison.
		return : bool
		'''
		if len(msg.embeds) > 0:
			if msg.embeds[0].title == self.title or msg.embeds[0].title == self.title_confirm:
				return True
			elif msg.embeds[0].title == self.title_history:
				await self.payement_status(msg)
				return False

	async def branche_raw_reaction_add(self, chan, msg_react, emoji):
		'''
		return : void
		'''
		if await self.is_branche_embed(msg_react):
			if emoji.name in self.bran_ctrl_emojis:
				from .Beer import Beer
				b = Beer(None)
				if emoji.name == self.bran_ctrl_emojis[2]:
				#cancelation
					await self.avort_message(msg_react)
					st_embeds = await b.get_embeds_storage(chan)
					await super().react_to_msg(st_embeds[0], b.action_emoji)
				elif emoji.name == self.bran_ctrl_emojis[0]:
				#validation
					if ((len(msg_react.reactions) > 2 and msg_react.embeds[0].title == self.title) \
						or (len(msg_react.reactions) > 3 and msg_react.embeds[0].title == self.title_confirm)):
						#start branche
						cancel = True
						for react in msg_react.reactions:
							if react.count > 1 and react.emoji not in self.ctrl_emojis:
								cancel = False
						if cancel:
							await self.avort_message(msg_react)
							st_embeds = await b.get_embeds_storage(chan)
							await super().react_to_msg(st_embeds[0], b.action_emoji)
						else:
							user = await super().who_react(msg_react.reactions)
							await self.valid_branche(msg_react, user[0])
					else:
						#confirm final branche and stop it
						beer = list()
						for emo in txt_random_emojis:
							if emo in msg_react.embeds[0].fields[0].name:
								beer.append(msg_react.embeds[0].fields[0].name[len(emo)+3:])
						beer.append(msg_react.embeds[0].fields[0].value)
						await msg_react.clear_reactions()
						await super().react_to_msg(msg_react, self.payement_emojis[0])
						await b.remove_beer(chan, beer, msg_react)
				elif emoji.name == self.bran_ctrl_emojis[1]: 
				#pencil
					await super().unlock_writing(chan, 1, msg_react)
					await msg_react.clear_reactions()
					await self.modify_branche(msg_react, -1)

	async def to_branche_send_message(self, message):
		if await super().find_txt_msg(message.channel, 3, self.begin_of_txt_ask_msg):
		#found an answer to the quantity of beer received 
			branche_setup_id = await super().find_id_in_msg(message.channel, GlobalString.id_identificator)
			branche_setup_msg = await message.channel.fetch_message(branche_setup_id)
			await self.modify_parameters(branche_setup_msg, message)
			
	async def init_branche(self, channel):
		from .Beer import Beer
		self.template = discord.Embed()
		await super().startup(self.branche_embed)
		self.template.remove_field(0) #empty stock
		Beer_obj = Beer(None)
		beer_stock = await super().find_embed_with_title(channel, 5, Beer_obj.beer_status_embed['title'])
		beers = await Beer_obj.get_beers(channel)
		if beers == None:
			await channel.send(":warning: Le stock de bières est vide.\n:x: **Opération annulée**", delete_after=7)
			await super().react_to_msg(beer_stock, Beer_obj.action_emoji)
		else:
			txt_list_emo = await super().get_random_emojis(len(beers), txt_random_emojis)
			list_emo = super().converter_text_to_emojis(txt_list_emo)
			for i in range(len(beers)):
				self.template.add_field(name=txt_list_emo[i]+' : '+beers[i][0]+' - '+beers[i][1], value=0)
			branche_setup_msg = await channel.send(embed=self.template)
			await super().react_to_msg(branche_setup_msg, list_emo+self.ctrl_emojis)

	async def valid_branche(self, branche_setup_msg, user_react):
		list_react = branche_setup_msg.reactions
		beer_target = None
		for react in list_react:
			if react.emoji not in self.bran_ctrl_emojis and react.count > 1 and beer_target == None:
				beer_target = branche_setup_msg.embeds[0].fields[list_react.index(react)].name
		if beer_target != None:
			branche_setup_msg.embeds[0].clear_fields()
			branche_setup_msg.embeds[0].add_field(name=beer_target, value=1)
			branche_setup_msg.embeds[0].set_footer(text='À Payé : '+self.payement_emojis[1]+'| Via : cash' \
			+'\nValider : '+self.bran_ctrl_emojis[0]+' Modifier : '+self.bran_ctrl_emojis[1]+' Annuler : '+self.bran_ctrl_emojis[2])
			dict_branche = branche_setup_msg.embeds[0].to_dict()
			dict_branche['description'] = 'Acheteur : Le Bar\nRaison: Pré-TD\nBrancheur: '+user_react.mention
			dict_branche['title'] = self.title_confirm
			new_embed_setup_msg = discord.Embed.from_dict(dict_branche)
			new_branche_setup_msg = await branche_setup_msg.edit(embed=new_embed_setup_msg)
			await branche_setup_msg.clear_reactions()
			await super().react_to_msg(branche_setup_msg, self.bran_ctrl_emojis)
		else:
			await super().avort_message(branche_setup_msg)

	async def modify_branche(self, branche_setup_msg, previous_question_num):
		q = self.modify_questions[previous_question_num+1]
		id = '||'+GlobalString.id_identificator+str(branche_setup_msg.id)+'||\n'
		msg = q[0] + '\nPar défaut : '
		if previous_question_num != 1:
			msg = msg + q[1]
		else:
			user = await super().who_writing(branche_setup_msg.channel, 1)
			msg = msg + user[0].mention
		msg = msg + " | *Tapez 'ok' si vous souhaitez conserver ce paramètre*"
		if q[2] is int:
			msg = msg + "\n**Veuillez entrer uniquement un nombre dans votre réponse, inférieur ou égal à la quantité disponible dans le stock**"
		await branche_setup_msg.channel.send(id+self.begin_of_txt_ask_msg+msg)

	async def modify_parameters(self, branche_setup_msg, message):
		answer = message.content
		question = await super().find_txt_msg(branche_setup_msg.channel, 3, self.begin_of_txt_ask_msg)
		question = question.content.split('\n')[1]
		question = question[len(self.begin_of_txt_ask_msg):]
		if question == self.modify_questions[0][0]:
			dict_branche = branche_setup_msg.embeds[0].to_dict()
			if answer.lower() != 'ok':
				dict_branche['description'] = 'Acheteur : '+answer
			else:
				dict_branche['description'] = 'Acheteur : Le Bar'
			new_embed_setup_msg = discord.Embed.from_dict(dict_branche)
			await branche_setup_msg.edit(embed=new_embed_setup_msg)
			await self.modify_branche(branche_setup_msg, 0)
		elif question == self.modify_questions[1][0]:
			dict_branche = branche_setup_msg.embeds[0].to_dict()
			if answer.lower() != 'ok':
				dict_branche['description'] = dict_branche['description'] + '\nRaison : '+answer
			else:
				dict_branche['description'] = dict_branche['description'] + '\nRaison : Pré-TD'
			new_embed_setup_msg = discord.Embed.from_dict(dict_branche)
			await branche_setup_msg.edit(embed=new_embed_setup_msg)
			await self.modify_branche(branche_setup_msg, 1)
		elif question == self.modify_questions[2][0]:
			dict_branche = branche_setup_msg.embeds[0].to_dict()
			if answer.lower() != 'ok':
				if len(message.mentions) > 0:
					user = message.mentions[0].mention
					dict_branche['description'] = dict_branche['description'] + '\nBrancheur : '+user
					new_embed_setup_msg = discord.Embed.from_dict(dict_branche)
					await branche_setup_msg.edit(embed=new_embed_setup_msg)	
					await self.modify_branche(branche_setup_msg, 2)
				else:
					await branche_setup_msg.channel.send("Je n'ai pas compris votre réponse. Veuillez identifier la personne en écrivant '@' et en selectionnant la personne dans la liste proposée.")
					await self.modify_branche(branche_setup_msg, 1)
			else:
				user = await super().who_writing(message.channel, 1)
				user = user[0].mention
				dict_branche['description'] = dict_branche['description'] + '\nBrancheur : '+user
				new_embed_setup_msg = discord.Embed.from_dict(dict_branche)
				await branche_setup_msg.edit(embed=new_embed_setup_msg)	
				await self.modify_branche(branche_setup_msg, 2)
			
		elif question == self.modify_questions[3][0]:
			if answer.lower() != 'ok':
				try:
					answer = int(answer)
					branche_setup_msg.embeds[0].set_field_at(0, name=branche_setup_msg.embeds[0].fields[0].name, value=str(answer))
					await branche_setup_msg.edit(embed=branche_setup_msg.embeds[0])
					await self.modify_branche(branche_setup_msg, 3)
				except ValueError:
					await branche_setup_msg.channel.send("Je n'ai pas compris votre réponse. Veuillez n'entrer qu'un nombre svp, rien d'autre.")
					await self.modify_branche(branche_setup_msg, 2)
			else:
				await self.modify_branche(branche_setup_msg, 3)
		elif question == self.modify_questions[4][0]:
			if answer.lower() != 'ok':
				branche_setup_msg.embeds[0].set_footer(text='À Payé : '+self.payement_emojis[1]+'| Via : '+answer)
			else:
				branche_setup_msg.embeds[0].set_footer(text='À Payé : '+self.payement_emojis[1]+'| Via : cash')
			await branche_setup_msg.edit(embed=branche_setup_msg.embeds[0])
			await self.end_modify(branche_setup_msg)
	
	async def end_modify(self, branche_setup_msg):
		await super().lock_writing(branche_setup_msg.channel, 1, await super().who_writing(branche_setup_msg.channel, 1))
		branche_setup_msg.embeds[0].set_footer(text=branche_setup_msg.embeds[0].footer.text + '\n' + self.footer_wPencil)
		await branche_setup_msg.edit(embed=branche_setup_msg.embeds[0])
		await super().cleanup(branche_setup_msg.channel, branche_setup_msg.id)
		await super().react_to_msg(branche_setup_msg, self.bran_ctrl_emojis)

	async def payement_status(self, branche_setup_history):
		time = '??:??'
		emoji = branche_setup_history.reactions[0].emoji
		await branche_setup_history.clear_reactions()
		if emoji == self.payement_emojis[0]:
			footer = "À Payé : " + self.payement_emojis[0]
			date = "Date de paiement le " + time
		elif emoji == self.payement_emojis[1]:
			footer = "À Payé : " + self.payement_emojis[1]
			date = ''
		old_footer = branche_setup_history.embeds[0].footer.text.split('|')
		branche_setup_history.embeds[0].set_footer(text=footer+'|'+old_footer[1].split('\n')[0]+'\n'+date+'\n'+old_footer[1].split('\n')[2])
		await branche_setup_history.edit(embed=branche_setup_history.embeds[0])
		if date == '':
			await super().react_to_msg(branche_setup_history, [self.payement_emojis[0]])
		else:
			time = await super().set_timeFTT(branche_setup_history.edited_at)
			branche_setup_history.embeds[0].set_footer(text=branche_setup_history.embeds[0].footer.text.split('??:??')[0]+time+branche_setup_history.embeds[0].footer.text.split('??:??')[1])
			await branche_setup_history.edit(embed=branche_setup_history.embeds[0])
			await super().react_to_msg(branche_setup_history, [self.payement_emojis[1]])
		
		
		