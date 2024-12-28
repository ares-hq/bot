import discord
from datetime import datetime


# Visual Helper Class
class State:
    VERSION = "v2.0.0"
    DEVELOPERS = "<@291420737204649985> and <@751915057973035058>"
    NAME = "FTCScout"
    AVATAR = "https://via.placeholder.com/150"
    SIGNATURE = f"Powered by {NAME} {VERSION}"
    CHANNELS = ["bot", "bot-channel", str(NAME).lower(), "ftc-scout", "scout", "ftc", "general"]
    COMMANDS ={
            "team": {
                "Description": "Displays team *FIRST* information",
                "Usage": "/team <team_number>"
            },
            "match": {
                "Description": "OPR-Based Match Prediction",
                "Usage": "/match <red_alliance> <blue_alliance>"
            },
            "favorite": {
                "Description": "Marks a team as the server favorite. Enter a team a second time to remove them from the list.",
                "Permissions Required": "Manage Nicknames",
                "Usage": "/favorite <team_number>"
            }
        }
    FIRST_BLACK = discord.Color(0x231F20)
    FIRST_BLUE = discord.Color(0x0066B3)
    FIRST_RED = discord.Color(0xED1C24)
    FIRST_GRAY = discord.Color(0x9A989A)
    FAVORITE = discord.Color(0xFFD700)

    REQUEST_TIME = datetime.now()

    @staticmethod
    def ERROR(title="Error", description="An error has occurred. Please try again later.") -> discord.Embed:
        
        color = discord.Color.red()
        embed = discord.Embed(title=title,description=description, color=color, timestamp=State.REQUEST_TIME)
        return embed
    
    @staticmethod
    def SUCCESS(title="Success", description="")-> discord.Embed:
        color = discord.Color.green()
        embed = discord.Embed(title=title, description=description, color=color, timestamp=State.REQUEST_TIME)
        return embed
    
    @staticmethod
    def WARNING(title="Warning", description = "Double check your input and try again. Information may be missing or incorrect.")-> discord.Embed:
        color = discord.Color.orange()
        embed = discord.Embed(title=title,description=description, color=color, timestamp=State.REQUEST_TIME)
        return embed
    
    @staticmethod
    def INFO(title="Info", description="")-> discord.Embed:
        color = discord.Color.blue()
        embed = discord.Embed(title=title,description=description, color=color, timestamp=State.REQUEST_TIME)
        return embed
    
    @staticmethod
    def ANNOUNCEMENT(title="Announcement", description="")-> discord.Embed:
        color = discord.Color.teal()
        embed = discord.Embed(title=title,description=description, color=color, timestamp=State.REQUEST_TIME)
        return embed