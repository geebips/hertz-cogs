from .hztools import hztools

async def setup(bot):
    cog = hztools(bot)
    bot.add_cog(cog)
    await cog.configuration()
