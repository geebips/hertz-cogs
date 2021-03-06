import discord
import asyncio
import aiohttp
import json
from aiohttp_socks import ProxyType, ProxyConnector, ChainProxyConnector
from redbot.core import Config, commands, checks
from redbot.core.utils.chat_formatting import pagify
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS

class hztools(commands.Cog):
	def __init__(self, bot):
		
		# Bot
		self.bot = bot  
		self.statuscount = 0
		self.thumbnail = "https://i.imgur.com/Q2Xk5Sp.gif"
		self.footerimg = "https://i.imgur.com/Q2Xk5Sp.gif"
		self.footer = "HzTools by Hertz#1234"

		# API Url(s)
		self.webresolver = "http://webresolver.nl/api.php"
		self.hackertarget = "https://api.hackertarget.com"
		self.c99 = "https://api.c99.nl"

		# Configuration
		default_global = {"WR_API_KEY": None, "EMOJI_ID": None, "C99_API_KEY": None, "PROXY_AUTH": None, "PROXY_INFO": None}		
		self.config = Config.get_conf(self, 2788801004)
		self.config.register_guild(**default_global)

	async def configuration(self) -> None:
		self.emoji = self.bot.get_emoji(await self.config.EMOJI_ID())
		self.c99_key = await self.config.C99_API_KEY()
		self.wr_key = await self.config.WR_API_KEY()
		auth, proxyinfo = await self.config.PROXY_AUTH(), await self.config.PROXY_INFO()
		if not auth and proxyinfo:
			self.session = aiohttp.ClientSession()
		if not auth:
			proxy = ProxyConnector.from_url("socks5://@"+proxyinfo)
			self.session = aiohttp.ClientSession()
		else:
			proxy = ProxyConnector.from_url("socks5://"+auth+"@"+proxyinfo)
			self.session = aiohttp.ClientSession(connector=proxy)

	
	##############################
	# Commands for Configuration #
	##############################
	@checks.is_owner()
	@commands.dm_only()
	@commands.group(pass_context=True) #group
	async def setup(self, ctx):
		"""Set API Keys for specific websites."""

	@setup.command(name="proxyip")
	async def _proxyip(self, ctx, IP: str, PORT: str):
		"""Set the proxy URL/IP:PORT to use, can be used without using `.setproxyauth` if the specified proxy doesn't require credentials."""
		if IP:
			await self.config.PROXY_INFO.set(IP+":"+PORT)
			embed = discord.Embed(color=await ctx.embed_color(), title="Proxy URL/IP set.").set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
			await ctx.send(embed=embed)
		
	@setup.command(name="proxyauth")
	async def _proxyauth(self, ctx, USER: str, PASS: str):
		"""Set the Proxy Authentication via user:pass. (USE `.setproxyip` FIRST!"""
		if USER:
			await self.config.PROXY_AUTH.set(USER+":"+PASS)
			embed = discord.Embed(color=await ctx.embed_color(), title="Proxy authentication set.").set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
			await ctx.send(embed=embed)

	@setup.command(name="emoji")
	async def _emoji(self, ctx, EMOJIID: int):
		"""Set the Embed Emoji."""
		if EMOJIID:
			await self.config.EMOJI_ID.set(EMOJIID)
			embed = discord.Embed(color=await ctx.embed_color(), title="Emoji ID set.").set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
			await ctx.send(embed=embed)

	@setup.command(name="setc99api", aliases=["setc99"])
	async def _setc99api(self, ctx, KEY: str):
		"""Set the API Key for c99.nl."""
		if KEY:
			await self.config.C99_API_KEY.set(KEY)
			embed = discord.Embed(color=await ctx.embed_color(), title="API Key set.").set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
			await ctx.send(embed=embed)

	@setup.command(name="setwrapi", aliases=["setwr"])
	async def _wrapi(self, ctx, KEY: str):
		"""Set the API Key for webresolver.nl"""
		if KEY:
			await self.config.WR_API_KEY.set(KEY)
			embed = discord.Embed(color=await ctx.embed_color(), title="Webresolver.nl API Key set").set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
			await ctx.send(embed=embed)

	####################
	# Non-API Commands #
	####################
	@commands.command(name="screenshare", aliases=["ss"])
	@commands.guild_only()
	async def _screenshare(self, ctx, member: discord.Member = None):
		"""Returns a link for screensharing in Voice Channels."""
		if member is None:
			member = ctx.author
		if member.voice is None:
			embed = discord.Embed(title="That user is not in a voice channel at the moment...")
			message = await ctx.send(embed=embed)
		else:
			await ctx.send(f"<https://discordapp.com/channels/{member.guild.id}/{member.voice.channel.id}>")


	############################
	# Webresolver.nl API Calls #
	############################

	@commands.command(name="whois")
	@commands.guild_only()
	async def _whois(self, ctx, URL: str):
		"""Get the registration information from a domain."""
		if not self.wr_key:
			embed = discord.Embed(color=await ctx.embed_color(), title="Error:", description="No Webresolver.nl Key set... Try `[p]setup setwrapi`").set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(color=await ctx.embed_color(), title=str(self.emoji))
		message = await ctx.send(embed=embed)
		async with ctx.typing():
			async with self.session.get(self.webresolver, params={"key": self.wr_key, "html": "0", "action": "whois", "string": URL}) as resp:
				pages = pagify(await resp.text(), page_length=2048)
				embeds = [
				discord.Embed(color=await ctx.embed_color(), title="Website Whois:", description=(page)).set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
				for page in pages
				]
				await message.delete()
				await menu(ctx, embeds, controls=DEFAULT_CONTROLS)

	@commands.command(name="icmp")
	@commands.guild_only()
	async def _icmp(self, ctx, IP: str):
		"""Shows how long it takes for packets to reach host."""
		if not self.wr_key:
			embed = discord.Embed(color=await ctx.embed_color(), title="Error:", description="No Webresolver.nl Key set... Try `[p]setup setwrapi`").set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(color=await ctx.embed_color(), title=str(self.emoji))
		message = await ctx.send(embed=embed)
		async with ctx.typing():
			async with self.session.get(self.webresolver, params={"key": self.wr_key, "html": "0", "action": "ping", "string": IP}) as resp:
				embed = discord.Embed(color=await ctx.embed_color(), title="Results:", description=await resp.text()).set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
				await message.edit(embed=embed)

	@commands.command(name="skype")
	@commands.guild_only()
	async def _skype(self, ctx, SKYPE: str):
		"""If the realtime resolver fails it will show you the last known IP."""
		if not self.wr_key:
			embed = discord.Embed(color=await ctx.embed_color(), title="Error:", description="No Webresolver.nl Key set... Try `[p]setup setwrapi`").set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(color=await ctx.embed_color(), title=str(self.emoji))
		message = await ctx.send(embed=embed)
		async with ctx.typing():
			async with self.session.get(self.webresolver, params={"key": self.wr_key, "html": "0", "action": "resolve", "string": SKYPE}) as resp:
				embed = discord.Embed(color=await ctx.embed_color(), title="Skype Results:", description=await resp.text()).set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
				await message.edit(embed=embed)

	@commands.command(name="skypedb")
	@commands.guild_only()
	async def _skypedb(self, ctx, SKYPE: str):
		"""If the realtime resolver fails it will show you the last known IP."""
		if not self.wr_key:
			embed=discord.Embed(color=await ctx.embed_color(), title="Error:", description="No Webresolver.nl Key set... Try `[p]setup setwrapi`").set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(color=await ctx.embed_color(), title=str(self.emoji))
		message = await ctx.send(embed=embed)
		async with ctx.typing():
			async with self.session.get(self.webresolver, params={"key": self.wr_key, "html": "0", "action": "resolvedb", "string": SKYPE}) as resp:
				embed = discord.Embed(color=await ctx.embed_color(), title="Skype DB Results:", description=await resp.text()).set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
				await message.edit(embed=embed)

	@commands.command(name="cloudflare", aliases=["cf"])
	@commands.guild_only()
	async def _cloudflare(self, ctx, URL: str):
		"""Bruteforce on the most common subdomains in order to search for the real IP."""
		if not self.wr_key:
			embed = discord.Embed(color=await ctx.embed_color(), title="Error:", description="No Webresolver.nl Key set... Try `[p]setup setwrapi`").set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(color=await ctx.embed_color(), title=str(self.emoji))
		message = await ctx.send(embed=embed)
		async with ctx.typing():
			async with self.session.get(self.webresolver, params={"key": self.wr_key, "html": "0", "action": "cloudflare", "string": URL}) as resp:
				embed = discord.Embed(color=await ctx.embed_color(), title="Cloudflare Info:", description=await resp.text()).set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
				await message.edit(embed=embed)

	@commands.command(name="geoip", aliases=["geo"])
	@commands.guild_only()
	async def _geoip(self, ctx, INPUT: str):
		"""Supports Domain, IPv4 and IPv6."""
		if not self.wr_key:
			embed = discord.Embed(color=await ctx.embed_color(), title="Error:", description="No Webresolver.nl Key set... Try `[p]setup setwrapi`").set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(color=await ctx.embed_color(), title=str(self.emoji))
		message = await ctx.send(embed=embed)
		async with ctx.typing():
			async with self.session.get(self.webresolver, params={"key": self.wr_key, "html": "0", "action": "geoip", "string": INPUT}) as resp:
				embed = discord.Embed(color=await ctx.embed_color(), title="Geolocation Results:", description=await resp.text()).set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
				await message.edit(embed=embed)

	@commands.command(name="headers")
	@commands.guild_only()
	async def _headers(self, ctx, URL: str):
		"""Get the website header information from a domain."""
		if not self.wr_key:
			embed = discord.Embed(color=await ctx.embed_color(), title="Error:", description="No Webresolver.nl Key set... Try `[p]setup setwrapi`").set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(color=await ctx.embed_color(), title=str(self.emoji))
		message = await ctx.send(embed=embed)
		await asyncio.sleep(1)
		async with ctx.typing():
			async with self.session.get(self.webresolver, params={"key": self.wr_key, "html": "0", "action": "header", "string": URL}) as resp:
				embed = discord.Embed(color=await ctx.embed_color(), title="Headers:", description=await resp.text()).set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
				await message.edit(embed=embed)

	@commands.command(name="portscan", aliases=["port"])
	@commands.guild_only()
	async def _portscan(self, ctx, PORT: str, IP: str):
		"""Scans a specific port on a defined IP."""
		if not self.wr_key:
			embed = discord.Embed(color=await ctx.embed_color(), title="Error:", description="No Webresolver.nl Key set... Try `[p]setup setwrapi`").set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(color=await ctx.embed_color(), title=str(self.emoji))
		message = await ctx.send(embed=embed)
		await asyncio.sleep(1)
		async with ctx.typing():
			async with self.session.get(self.webresolver, params={"key": self.wr_key, "html": "0", "action": "portscan", "string": IP, "port": PORT}) as resp:
				embed = discord.Embed(color=await ctx.embed_color(), title="Port Scan Results:", description=await resp.text()).set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
				await message.edit(embed=embed)

	@commands.command(name="ip2skype", aliases=["i2s"])
	@commands.guild_only()
	async def _i2s(self, ctx, IP: str):
		"""Tries to find any websites linked to the IP you entered."""
		if not self.wr_key:
			embed = discord.Embed(color=await ctx.embed_color(), title="Error:", description="No Webresolver.nl Key set... Try `[p]setup setwrapi`").set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(color=await ctx.embed_color(), title=str(self.emoji))
		message = await ctx.send(embed=embed)
		async with ctx.typing():
			async with self.session.get(self.webresolver, params={"key": self.wr_key, "html": "0", "action": "ip2websites", "string": IP}) as resp:
				embed = discord.Embed(color=await ctx.embed_color(), title="IP to Skype:", description=await resp.text()).set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
				await message.edit(embed=embed)

	@commands.command(name="email2skype", aliases=["e2s"])
	@commands.guild_only()
	async def _emailtoskype(self, ctx, EMAIL: str):
		"""Get all Skype accounts which are connected to a specific email."""
		if not self.wr_key:
			embed = discord.Embed(color=await ctx.embed_color(), title="Error:", description="No Webresolver.nl Key set... Try `[p]setup setwrapi`").set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(color=await ctx.embed_color(), title=str(self.emoji))
		message = await ctx.send(embed=embed)
		async with ctx.typing():
			async with self.session.get(self.webresolver, params={"key": self.wr_key, "html": "0", "action": "phonenumbercheck", "string": EMAIL}) as resp:
				embed = discord.Embed(color=await ctx.embed_color(), description=await resp.text()).set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
				await message.edit(embed=embed)

	@commands.command(name="skype2email", aliases=["s2e"])
	@commands.guild_only()
	async def _skypetoemail(self, ctx, SKYPE: str):
		"""Get all emails linked to a Skype account."""
		if not self.wr_key:
			embed = discord.Embed(color=await ctx.embed_color(), title="Error:", description="No Webresolver.nl Key set... Try `[p]setup setwrapi`").set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(color=await ctx.embed_color(), title=str(self.emoji))
		message = await ctx.send(embed=embed)
		async with ctx.typing():
			async with self.session.get(self.webresolver, params={"key": self.wr_key, "html": "0", "action": "skype2email", "string": SKYPE}) as resp:
				embed = discord.Embed(color=await ctx.embed_color(), title="Skype to Email:", description=await resp.text()).set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
				await message.edit(embed=embed)

	@commands.command(name="phone")
	@commands.guild_only()
	async def _phone(self, ctx, NUMBER: str):
		"""Looks up information about a specific phone number. (Use international phone format)."""
		if not self.wr_key:
			embed=discord.Embed(color=await ctx.embed_color(), title="Error:", description="No Webresolver.nl Key set... Try `[p]setup setwrapi`").set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(color=await ctx.embed_color(), title=str(self.emoji))
		message = await ctx.send(embed=embed)
		async with ctx.typing():
			async with self.session.get(self.webresolver, params={"key": self.wr_key, "html": "0", "action": "phonenumbercheck", "string": NUMBER}) as resp:
				embed = discord.Embed(color=await ctx.embed_color(), title="Phone Information:", description=await resp.text()).set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
				await message.edit(embed=embed)

	@commands.command(name="disposable", aliases=["demails"])
	@commands.guild_only()
	async def _disposable(self, ctx, EMAIL: str):
		"""Search through a database with known disposable email servers to check if a domain is disposable."""
		if not self.wr_key:
			embed = discord.Embed(color=await ctx.embed_color(), title="Error:", description="No Webresolver.nl Key set... Try `[p]setup setwrapi`").set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(color=await ctx.embed_color(), title=str(self.emoji))
		message = await ctx.send(embed=embed)
		async with ctx.typing():
			async with self.session.get(self.webresolver, params={"key": self.wr_key, "html": "0", "action": "disposable_email", "string": EMAIL}) as resp:
				embed = discord.Embed(color=await ctx.embed_color(), title="Disposable Email Results:", description=await resp.text()).set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
				await message.edit(embed=embed)
	
	@commands.command(name="domain")
	@commands.guild_only()
	async def _domain(self, ctx, URL: str):
		"""Get all the information from a domain such as: IP history, subdomains & domain score."""
		if not self.wr_key:
			embed = discord.Embed(color=await ctx.embed_color(), title="Error:", description="No Webresolver.nl Key set... Try `[p]setup setwrapi`").set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(color=await ctx.embed_color(), title=str(self.emoji))
		message = await ctx.send(embed=embed)
		async with ctx.typing():
			async with self.session.get(self.webresolver, params={"key": self.wr_key, "html": "0", "action": "domain", "string": URL}) as resp:
				pages = pagify(await resp.text(), page_length=600)
				embeds = [
				discord.Embed(color=await ctx.embed_color(), title="Domain Information:", description=(page)).set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
				for page in pages
				]
				await message.delete()
				await menu(ctx, embeds, controls=DEFAULT_CONTROLS)

	##########################
	# Hackertarget API Calls #
	##########################
	@commands.command(name="mtr")
	@commands.guild_only()
	async def _mtr(self, ctx, IP: str):
		"""Examine the hops that communication will follow across an IP network."""
		if not self.wr_key:
			embed = discord.Embed(color=await ctx.embed_color(), title="Error:", description="No Webresolver.nl Key set... Try `[p]setup setwrapi`").set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(color=await ctx.embed_color(), title=str(self.emoji))
		message = await ctx.send(embed=embed)
		async with ctx.typing():
			async with self.session.get(self.hackertarget+'/mtr/', params={"key": self.wr_key, "q": IP}) as resp:
				embed = discord.Embed(color=await ctx.embed_color(), title="MTR Results:", description=await resp.text()).set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
				await message.edit(embed=embed)

	####################
	# C99.nl API Calls #
	####################
	@commands.command(name="nmap", aliases=["scan"])
	@commands.guild_only()
	async def _nmap(self, ctx, IP: str):
		"""Scan common ports to see if any are open/closed."""
		if not self.c99_key:
			embed = discord.Embed(color=await ctx.embed_color(), title="Error:", description="No C99.nl Key set... Try `[p]setup setc99api`").set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(color=await ctx.embed_color(), title=str(self.emoji))
		message = await ctx.send(embed=embed)
		async with ctx.typing():
			async with self.session.get(self.c99+'/nmap', params={"key": self.c99_key, "host": IP}) as resp:
				pages = pagify(await resp.text(), page_length=600)
				embeds = [
				discord.Embed(color=await ctx.embed_color(), title="Domain Information:", description=(page)).set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
				for page in pages
				]
				await message.delete()
				await menu(ctx, embeds, controls=DEFAULT_CONTROLS)

	@commands.command(name="fakename", aliases=["fake"])
	@commands.guild_only()
	async def _fakename(self, ctx, GENDER: str):
		"""Generates fake information to use."""
		if not self.c99_key:
			embed = discord.Embed(color=await ctx.embed_color(), title="Error:", description="No C99.nl Key set... Try `[p]setup setc99api`").set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(color=await ctx.embed_color(), title=str(self.emoji))
		message = await ctx.send(embed=embed)
		async with ctx.typing():
			async with self.session.get(self.c99+'/randomperson', params={"key": self.c99_key, "gender": GENDER, "json": "json"}) as resp:
				data = await resp.json()
				embed=discord.Embed(color=await ctx.embed_color()).set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
				embed.add_field(name='Name:', value=data['name'], inline=True).add_field(name='\u200B', value='\u200B', inline=True).add_field(name='\u200B', value='\u200B', inline=True)
				embed.add_field(name='Age:', value=data['age'], inline=True)
				embed.add_field(name='DOB:', value=data['dob'], inline=True).add_field(name='\u200B', value='\u200B', inline=True)
				embed.add_field(name='City:', value=data['city'], inline=True)
				embed.add_field(name='Country:', value=data['country'], inline=True).add_field(name='\u200B', value='\u200B', inline=True)
				embed.add_field(name='State:', value=data['state'], inline=True)
				embed.add_field(name='ZIP:', value=data['zip'], inline=True).add_field(name='\u200B', value='\u200B', inline=True)
				embed.add_field(name='Home Phone:', value=data['phone'], inline=True)
				embed.add_field(name='Cell Phone:', value=data['cell'], inline=False)
				embed.add_field(name='Email:', value=data['email'], inline=False)
				await message.edit(embed=embed)  

	@commands.command(name="ytmp3")
	@commands.guild_only()
	async def _ytmp3(self, ctx, ID: str):
		"""Convert a Youtube video to an MP3 by ID."""
		if not self.c99_key:
			embed = discord.Embed(color=await ctx.embed_color(), title="Error:", description="No C99.nl Key set... Try `[p]setup setc99api`").set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(color=await ctx.embed_color(), title=str(self.emoji))
		message = await ctx.send(embed=embed)
		async with ctx.typing():
			async with self.session.get(self.c99+'/youtubemp3', params={"key": self.c99_key, "videoid": ID, "json": "json"}) as resp:
				data = await resp.json()
				await message.delete()
				await ctx.send(data['url'])

	@commands.command(name="btcbalance", aliases=["btcbal"])
	@commands.guild_only()
	async def _btcbalance(self, ctx, ADDRESS: str):
		"""Checks the current balance of any Bitcoin address."""
		if not self.c99_key:
			embed = discord.Embed(color=await ctx.embed_color(), title="Error:", description="No C99.nl Key set... Try `[p]setup setc99api`").set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(color=await ctx.embed_color(), title=str(self.emoji))
		message = await ctx.send(embed=embed)
		async with ctx.typing():
			async with self.session.get(self.c99+'/bitcoinbalance', params={"key": self.c99_key, "address": ADDRESS}) as resp:
				embed = discord.Embed(color=await ctx.embed_color(), title=await resp.text()).set_thumbnail(url=self.thumbnail).set_author(name="BTC", icon_url="https://i.imgur.com/uuZLtm6.png").set_footer(text=self.footer, icon_url=self.footerimg)
				await message.edit(embed=embed)

	@commands.command(name="ethereumbalance", aliases=["ethbal"])
	@commands.guild_only()
	async def _etheriumbalance(self, ctx, ADDRESS: str):
		"""Checks the current balance of any Etherium address."""
		if not self.c99_key:
			embed = discord.Embed(color=await ctx.embed_color(), title="Error:", description="No C99.nl Key set... Try `[p]setup setc99api`").set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(color=await ctx.embed_color(), title=str(self.emoji))
		message = await ctx.send(embed=embed)
		async with ctx.typing():
			async with self.session.get(self.c99+'/ethereumbalance', params={"key": self.c99_key, "address": ADDRESS}) as resp:
				embed = discord.Embed(color=await ctx.embed_color(), description=await resp.text()).set_thumbnail(url=self.thumbnail).set_author(name="Etherium", icon_url="https://i.imgur.com/bJO1SSN.png").set_footer(text=self.footer, icon_url=self.footerimg)
				await message.edit(embed=embed)

	@commands.command(name="screenshot", aliases=["sshot"])
	@commands.guild_only()
	async def _screenshot(self, ctx, URL: str):
		"""Returns a screenshot link of said website."""
		if not self.c99_key:
			embed = discord.Embed(color=await ctx.embed_color(), title="Error:", description="No C99.nl Key set... Try `[p]setup setc99api`").set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(color=await ctx.embed_color(), title=str(self.emoji))
		message = await ctx.send(embed=embed)
		async with ctx.typing():
			async with self.session.get(self.c99+'/createscreenshot', params={"key": self.c99_key, "url": URL}) as resp:
				if "Invalid" in await resp.text():
					embed = discord.Embed(color=await ctx.embed_color(), title="Invalid Syntax", description="Example: https://google.com").set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
					await message.edit(embed=embed)
				else:
					embed = discord.Embed(color=await ctx.embed_color(), title="Website Screenshot:", description="The screenshots may not work with some websites which have a firewall such as Cloudflare or DDOSGuard.").set_thumbnail(url=self.thumbnail).set_image(url=await resp.text()).set_footer(text=self.footer, icon_url=self.footerimg)
					await message.edit(embed=embed)

	@commands.command(name="gifd")
	@commands.guild_only()
	async def _gifd(self, ctx, KEYWORD: str):
		"""Random GIF."""
		if not self.c99_key:
			embed = discord.Embed(color=await ctx.embed_color(), title="Error:", description="No C99.nl Key set... Try `[p]setup setc99api`").set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(color=await ctx.embed_color(), title=str(self.emoji))
		message = await ctx.send(embed=embed)
		avatar = message.author.avatar_url if message.author.avatar else bot.user.default_avatar_url
		async with ctx.typing():
			async with self.session.get(self.c99+'/gif', params={"key": self.c99_key, "keyword": KEYWORD, "json": "json"}) as resp:
				if "No images found." in await resp.text():
					embed = discord.Embed(color=await ctx.embed_color(), title="No images found.", description="There were no images found by that keyword, please try using a similar keyword.").set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
					await message.edit(embed=embed)
				else:
					data = await resp.json()
					result = data['images']
					embeds = [
					discord.Embed(color=await ctx.embed_color(), description="Heres your random GIF:").set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg).set_image(url=(image)).set_author(name=ctx.author, icon_url=avatar)
					for image in result
					]
					await message.delete()
					await menu(ctx, embeds, controls=DEFAULT_CONTROLS)

	@commands.command(name="proxylist")
	@commands.guild_only()
	async def _proxylist(self, ctx, TYPE: str, COUNTRY: str, ANONYMITY: str, LIMIT: int):
		"""Get a list of fresh http, https, socks4, socks5 proxies."""
		if not self.c99_key:
			embed = discord.Embed(color=await ctx.embed_color(), title="Error:", description="No C99.nl Key set... Try `[p]setup setc99api`").set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(color=await ctx.embed_color(), title=str(self.emoji))
		message = await ctx.send(embed=embed)
		async with ctx.typing():
			async with self.session.get(self.c99+'/proxylist', params={"key": self.c99_key, "type": TYPE, "anonimity": ANONYMITY, "country": COUNTRY, "limit": LIMIT, "json": "json"}) as resp:
				data = await resp.json()
				embeds = [
				discord.Embed(color=await ctx.embed_color(), title="Proxy List:", description=page).set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
				for page in pagify("\n".join(data['proxies']), page_length=500)
				]
				await message.delete()
				await menu(ctx, embeds, controls=DEFAULT_CONTROLS)
		
	@commands.command(name="checkdomain")
	@commands.guild_only()
	async def _checkdomain(self, ctx, DOMAIN: str):
		"""Checks whether or not a specific domain."""
		if not self.c99_key:
			embed = discord.Embed(color=await ctx.embed_color(), title="Error:", description="No C99.nl Key set... Try `[p]setup setc99api`").set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(color=await ctx.embed_color(), title=str(self.emoji))
		message = await ctx.send(embed=embed)
		async with ctx.typing():
			async with self.session.get(self.c99+'/domainchecker', params={"key": self.c99_key, "domain": DOMAIN}) as resp:
				embed = discord.Embed(color=await ctx.embed_color(), title="Domain Availability:", description=await resp.text()).set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
				await message.edit(embed=embed)

	@commands.command(name="define")
	@commands.guild_only()
	async def _define(self, ctx, WORD: str):
		"""Defines specified word."""
		if not self.c99_key:
			embed = discord.Embed(color=await ctx.embed_color(), title="Error:", description="No C99.nl Key set... Try `[p]setup setc99api`").set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(color=await ctx.embed_color(), title=str(self.emoji))
		message = await ctx.send(embed=embed)
		async with ctx.typing():
			async with self.session.get(self.c99+'/dictionary', params={"key": self.c99_key, "word": WORD}) as resp:
				embed = discord.Embed(color=await ctx.embed_color(), title="Definition:", description=await resp.text()).set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
				await message.edit(embed=embed)

	@commands.command(name="translate")
	@commands.guild_only()
	async def _define(self, ctx, INPUT: str, LANG: str):
		"""Translates specified word/sentence to a specified language ie. EN, use quotes if you're going to translate a sentence."""
		if not self.c99_key:
			embed=discord.Embed(color=await ctx.embed_color(), title="Error:", description="No C99.nl Key set... Try `[p]setup setc99api`").set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(color=await ctx.embed_color(), title=str(self.emoji))
		message = await ctx.send(embed=embed)
		avatar = message.author.avatar_url if message.author.avatar else bot.user.default_avatar_url
		async with ctx.typing():
			async with self.session.get(self.c99+'/translate', params={"key": self.c99_key, "text": INPUT, "tolanguage": LANG}) as resp:
				embed = discord.Embed(color=await ctx.embed_color(), description=await resp.text()).set_author(name=ctx.author, icon_url=avatar).set_thumbnail(url=self.thumbnail).set_footer(text=self.footer, icon_url=self.footerimg)
				await message.edit(embed=embed)
