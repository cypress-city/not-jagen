import discord
from discord.ext import commands
from modules.core import Bot


class SampleCog(commands.Cog):
    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

    @discord.app_commands.command(
        name="sample",
        description="Does nothing."
    )
    async def sample_command(self, inter: discord.Interaction):
        pass


async def setup(bot: Bot):
    await bot.add_cog(SampleCog(bot))
