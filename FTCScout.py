import discord
import re
import requests
from datetime import datetime

def handle_user_messages(msg) ->str:
    message = msg.lower()
    if extractTeamNumbers(message):
        year = extractYear(message)
        numbers = extractTeamNumbers(message)
        
        if numbers is not None:
            totalString = f'**The following was found for team {", ".join(numbers)} in season {year}-{year+1}:** \n'
            totalString += FTCScoutBot(numbers, year=year)
            return totalString
        return 'Please enter a team number'
    elif 'help' == message:
        return f"-Use the format: 'team: XXX' to get team data. \n-Year is default to current season. To retrieve data from past year use format: 'Team XXX Year XXXX' to get team data for that year."
    
def extractTeamNumbers(msg: str) -> list:
    message = msg.lower()
    
    if 'team' in message:
        numbers = re.findall(r'team\s?(\d+)', message)
        return numbers if numbers else None
    
    return None

def extractYear(message):
    year_match = re.search(r'year\s?(\d{4})', message)
    year = findYear()
    if year_match:
        year = int(year_match.group(1))
    return year

async def processMessage(message):
    try:
        botfeedback = handle_user_messages(message.content)
        if botfeedback:
            await message.channel.send(botfeedback)
    except Exception as error:
        print(error)

def runBot():
    discord_token = 'MTIxNDY3Nzk5NzYxNzk0MjYyOA.GdgxVI.MSen_KE5fEf49q5ZKONgK20dBjyhug_HCEiVa4'
    intents = discord.Intents.default()
    intents.typing = False
    intents.message_content = True
    intents.presences = False
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print({client.user}, 'is live')
        await client.change_presence(activity=discord.Game('Christian Sucks!'))

    @client.event
    async def on_message(message):
        specific_channel_id = 1214714987638034545 
        specific_channel_id2 = 1214734647695646754
        #specific_channel_id = 1214734647695646754  #this is the testing one
        
        if message.channel.id == specific_channel_id:
            if message.author == client.user:
                return
            await processMessage(message)
        
        if message.channel.id == specific_channel_id2:
            if message.author == client.user:
                return
            await processMessage(message)

    client.run(discord_token)

def findYear():
    current_date = datetime.now()

    if current_date.month < 8:
        season_year = current_date.year - 1
    else:
        season_year = current_date.year
        
    return season_year
    
def FTCScoutBot(teamNumber, year=findYear()):
    team_number = int("".join(map(str, teamNumber))) if teamNumber else None
    url = "https://api.ftcscout.org/graphql"

    graphql_query = f"""
    query GetTeamByNumber($teamNumber: Int!) {{
        teamByNumber(number: $teamNumber) {{
            name
            quickStats(season: {year}) {{
                auto {{
                    rank
                    value
                }}
                eg {{
                    rank
                    value
                }}
                dc {{
                    rank
                    value
                }}
                tot {{
                    rank
                    value
                }}
            }}
            sponsors
            location {{
                city
                country
            }}
            updatedAt
        }}
    }}
    """

    variables = {
        "teamNumber": team_number
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, json={"query": graphql_query, "variables": variables}, headers=headers)

    try:
        json_data = response.json()

        if 'data' in json_data:
            team_data = json_data['data']['teamByNumber']
            team_name = team_data['name']
            sponsors = ", ".join(team_data['sponsors']) if team_data['sponsors'] else 'None'
            location_city = team_data['location']['city']
            location_country = team_data['location']['country']
            updatedAt = team_data['updatedAt']
            dt = datetime.strptime(updatedAt, "%Y-%m-%dT%H:%M:%S.%fZ")
            formatted_date_time = dt.strftime("%m-%d-%Y %H:%M")

            auto_rank = team_data['quickStats']['auto']['rank']
            auto_value = team_data['quickStats']['auto']['value']
            eg_rank = team_data['quickStats']['eg']['rank']
            eg_value = team_data['quickStats']['eg']['value']
            dc_rank = team_data['quickStats']['dc']['rank']
            dc_value = team_data['quickStats']['dc']['value']
            tot_rank = team_data['quickStats']['tot']['rank']
            tot_value = team_data['quickStats']['tot']['value']

            # old string dont touch its old
            # result_string = f"Team Name: {team_name}\nAuto Rank: {auto_rank}\nAuto OPR: {round(auto_value, 2)}\nEG Rank: {eg_rank}\nEG OPR: {round(eg_value, 2)}\nTeleOp Rank: {dc_rank}\nTeleOp OPR: {round(dc_value, 2)}\nOverall Rank: {tot_rank}\nOverall OPR: {round(tot_value, 2)}\nSponsors: {sponsors}\nLocation: {location_city}, {location_country}\nUpdated At: {formatted_date_time}"
            def bold_after_colon_plain(line):
                if ":" in line:
                    key, value = line.split(":", 1)
                    return f"**{key}**: {value.strip()}"
                return line

            lines = [
                f"Team Name: {team_name}",
                f"Auto Rank: {auto_rank}",
                f"Auto OPR: {round(auto_value, 2)}",
                f"EG Rank: {eg_rank}",
                f"EG OPR: {round(eg_value, 2)}",
                f"TeleOp Rank: {dc_rank}",
                f"TeleOp OPR: {round(dc_value, 2)}",
                f"Overall Rank: {tot_rank}",
                f"Overall OPR: {round(tot_value, 2)}",
                f"Sponsors: {sponsors}",
                f"Location: {location_city}, {location_country}",
                f"Updated At: {formatted_date_time}",
            ]

            result_string = "\n".join(bold_after_colon_plain(line) for line in lines)
            if(team_number == 14584):
                result_string += "\n🥳🧑‍🚀🚀"
        else:
            result_string = "No data found for the specified team number."

    except Exception as e:
        if str(e) == "'NoneType' object is not subscriptable":
            result_string = f"Team has no data for the {year}-{year+1} season. Please try again later."
        else:
            result_string = f"Error processing API response: {str(e)}"

    return result_string

if __name__ =='__main__':
    runBot()