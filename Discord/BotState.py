import discord
from datetime import datetime


# Visual Helper Class
class BotState:
    def __init__(self):
        pass

    @property
    def VERSION(self):
        return "v2.0.0"
    
    @property
    def DEVELOPERS(self):
        return "<@291420737204649985> and <@751915057973035058>"
    
    @property
    def BOT_NAME(self):
        return "FTCScout Bot"
    
    @property
    def BOT_AVATAR(self):
        return "https://via.placeholder.com/150"
    
    @property
    def REQUEST_TIME(self):
        return datetime.now()
    
    @property
    def ERROR(self):
        description = "An error occurred while processing the request. Try again later."
        color = discord.Color.red()
        embed = discord.Embed(title="ERROR",description=description, color=color, timestamp=self.REQUEST_TIME)
        return embed
    
    @property
    def SUCCESS(self):
        description = "Request Successfull!"
        color = discord.Color.green()
        embed = discord.Embed(title="SUCCESS",description=description, color=color, timestamp=self.REQUEST_TIME)
        return embed
    
    @property
    def WARNING(self):
        description = "Double check your input and try again. Information may be missing or incorrect."
        color = discord.Color.orange()
        embed = discord.Embed(title="WARNING",description=description, color=color, timestamp=self.REQUEST_TIME)
        return embed