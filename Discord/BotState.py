import discord
from datetime import datetime


# Visual Helper Class
class State:
    VERSION = "v2.0.0"
    DEVELOPERS = "<@291420737204649985> and <@751915057973035058>"
    NAME = "ARES"
    AVATAR = "https://via.placeholder.com/150"
    SIGNATURE = f"Powered by {NAME} {VERSION}"
    CHANNELS = ["bot", "bot-channel", str(NAME).lower(), "ares", "scout", "ftc", "general"]
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
                "Usage": "/favorite <team_number>"
            }
        }
    BROWSER = "edge"
    
    # COLOR SOURCE: https://www.firstinspires.org/sites/default/files/uploads/resource_library/brand/first-brand-guidelines-2020.pdf
    
    # CORE COLOR PALLETTE
    FIRST_BLACK = discord.Color(0x231F20)
    FIRST_BLUE = discord.Color(0x0066B3)
    FIRST_GRAY = discord.Color(0x9A989A)

    # LEAGUE SPECIFIC COLOR PALLETTE
    # FIRST LEGO LEAGUE
    DISCOVER_PURPLE = discord.Color(0x662D91) # DISCOVER
    EXPLORE_GREEN = discord.Color(0x00A651)  # EXPLORE
    CHALLENGE_RED = discord.Color(0xED1C24) # CHALLENGE
    # FIRST TECH CHALLENGE
    TECH_ORANGE = discord.Color(0xF57E25)
    # FIRST ROBOTICS COMPETITION
    ROBOT_BLUE = discord.Color(0x009CD7)

    # CUSTOM COLOR PALLETTE
    WHITE = discord.Color(0xFFFFFF)
    FAVORITE = discord.Color(0xFFD700)

    REQUEST_TIME = datetime.now()

    @staticmethod
    def ERROR(title="Error", description="An error has occurred. Please try again later.") -> discord.Embed:
        
        color = State.CHALLENGE_RED
        embed = discord.Embed(title=title,description=description, color=color, timestamp=State.REQUEST_TIME)
        return embed
    
    @staticmethod
    def SUCCESS(title="Success", description="")-> discord.Embed:
        color = State.EXPLORE_GREEN
        embed = discord.Embed(title=title, description=description, color=color, timestamp=State.REQUEST_TIME)
        return embed
    
    @staticmethod
    def WARNING(title="Warning", description = "Double check your input and try again. Information may be missing or incorrect.")-> discord.Embed:
        color = State.TECH_ORANGE
        embed = discord.Embed(title=title,description=description, color=color, timestamp=State.REQUEST_TIME)
        return embed
    
    @staticmethod
    def INFO(title="Info", description="")-> discord.Embed:
        color = State.FIRST_BLUE
        embed = discord.Embed(title=title,description=description, color=color, timestamp=State.REQUEST_TIME)
        return embed
    
    @staticmethod
    def ANNOUNCEMENT(title="Announcement", description="")-> discord.Embed:
        color = discord.Color.teal()
        embed = discord.Embed(title=title,description=description, color=color, timestamp=State.REQUEST_TIME)
        return embed