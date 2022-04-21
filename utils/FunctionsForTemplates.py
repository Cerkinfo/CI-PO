import discord
from discord.ext import commands

import emojis
from EmojisList import *

class FunctionsForTemplates:

	def add_zero_to_time(self, time):
		if time < 10: return '0'+str(time)
		else: return str(time)

	async def set_timeFTT(self, datetime): # default = UTC !
		hour = int(datetime.hour)
		if hour >= 22: hour -= 22
		else: hour += 2
		return self.add_zero_to_time(datetime.day) + '/' + self.add_zero_to_time(datetime.month) + '/' + str(datetime.year)[2:] + ' - ' \
		+ self.add_zero_to_time(hour) + ':' + self.add_zero_to_time(datetime.minute)

	async def not_active(self, ctx):
		if ctx.channel.topic == None or ctx.channel.topic[:len(GlobalString.gesTypeTopic)] != GlobalString.gesTypeTopic:
			return True

	async def good_command(self, ctx):
		if ctx.channel.topic != None and ctx.channel.topic[:len(GlobalString.gesTypeTopic)+len(ctx.command.name)] == GlobalString.gesTypeTopic+ctx.command.name:
			return True

	async def good_templates(self, ctx, name):
		if ctx.channel.topic != None and ctx.channel.topic[:len(GlobalString.gesTypeTopic)+len(ctx.command.name)] == name:
			return True

	async def lock_channel(self, ctx):
		await ctx.channel.set_permissions(ctx.guild.default_role, read_messages=True, send_messages=False, add_reactions=False, external_emojis=False)

	async def startup(self, informations=dict):
		self.template = discord.Embed(title=informations['title'], description=informations['description'], color=informations['color'])
		self.template.set_author(name=informations['author'], icon_url=informations['icon'].split('?')[0]) #remove img size printing
		self.template.set_thumbnail(url=informations['thumbnail'])
		self.template.add_field(name=informations['empty_stock'], value=0)
		self.template.set_footer(text=informations['footer'])

	async def who_react(self, reactions):
		for react in reactions:
			if react.count > 1:
				keep = react
		users = [user async for user in keep.users()]
		ret = list()
		for user in users:
			if not user.bot:
				ret.append(user)
		return ret

	async def unlock_writing(self, channel, num_authorized, msg_react):
		users = await self.who_react(msg_react.reactions)
		for user in users:
			if num_authorized > 0:
				await channel.set_permissions(user, send_messages=True)
				num_authorized = num_authorized - 1

	async def lock_writing(self, channel, num_authorized, members):
		for member in members:
			if not member.bot and num_authorized > 0:
				await channel.set_permissions(member, send_messages=False)
				num_authorized = num_authorized - 1

	async def who_writing(self, channel, num_authorized):
		hist = channel.history(limit=5)
		ret = list()
		async for msg in hist:
			if not msg.author.bot:
				ret.append(msg.author)
		return ret[:num_authorized]

	async def avort_message(self, msg):
		await msg.delete()

	async def empty_stock(self, embed_msg, empty_title):
		if len(embed_msg.fields) == 0:
			embed_msg.add_field(name=empty_title, value=0)

	async def get_message_got_reaction(self, payload=discord.RawReactionActionEvent):
		chan = self.bot.get_channel(payload.channel_id)
		msg = await chan.fetch_message(payload.message_id)
		return msg

	def converter_text_to_emojis(self, text):
		switcher = {
			list: text,
			str: [text]
		}
		text = switcher.get(type(text), TypeError)
		emoret = list()
		for emotxt in text:
			tmp = emojis.encode(emotxt)
			emoret.append(tmp)
		return emoret

	async def react_to_msg(self, msg, list_emo):
		for emo in list_emo:
			await msg.add_reaction(emo)
	
	async def get_random_emojis(self, nbre=int, emojis_list=list):
		from random import randint
		ret = list()
		while len(ret) < nbre:
			emo = emojis_list[randint(0,len(emojis_list)-1)]
			if emo not in ret:
				ret.append(emo)
		return ret

	async def get_random_emojis_in_fields(self, embed=discord.Embed, emojis_list=list):
		ret = list
		for field in embed.fields:
			for emo in emojis_list:
				if emo in field.name:
					ret.append(emo)
		return ret
	
	async def cleanup(self, channel, roof_msg_id=int, limit=20):
		hist = channel.history(limit=limit)
		loop = True
		async for msg in hist:
			if msg.id != roof_msg_id and loop:
				await msg.delete()
			else:
				loop = False

	async def find_id_in_msg(self, channel, heading_txt, txt=None):
		if txt is None:
			hist = channel.history(limit=2)
			async for msg in hist:
				if heading_txt in msg.content:
					txt = msg.content
		id_ = txt.split('\n')[0].split('||')[1]
		id_ = id_[len(heading_txt):]
		return id_

	async def find_embed_with_title(self, channel, limit, title_embed):
		hist = channel.history(limit=limit)
		async for msg in hist:
			if len(msg.embeds) > 0:
				if msg.embeds[0].title == title_embed:
					return msg

	async def find_txt_msg(self, channel, limit, txt_in_msg):
		hist = channel.history(limit=limit)
		async for msg in hist:
			if txt_in_msg in msg.content:
				return msg

	async def find_field_in_embed_name(self, embed_msg, informations):
		if type(informations) is str:
			list_ = embed_msg.fields
			for field in list_:
				if informations in field.name:
					return field, list_.index(field)
		elif type(informations) in (tuple, list):
			ret = list()
			for field in embed_msg.fields:
				r = list()
				for info in informations:
					if info in field.name:
						r.append(True)
					else:
						r.append(False)
				ret.append(r)
			for r in ret:
				if False in r:
					pass
				else:
					return embed_msg.fields[ret.index(r)], ret.index(r)