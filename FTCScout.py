import discord
import re
import requests

def handle_user_messages(msg) ->str:
    message = msg.lower()
    if'team' in message:
        numbers = extract_numbers_from_team_message(message)
        if numbers is not None:
            totalString = f'The following was found for team {", ".join(numbers)}: \n'
            totalString += FTCScoutBot(numbers)
            return totalString
        return 'Please enter a team number'
    else:
        return "Invalid command. Please use the 'team: XXX' format."
    
def extract_numbers_from_team_message(msg: str) -> list:
    message = msg.lower()
    
    if 'team' in message:
        # Use regular expression to find numbers
        numbers = re.findall(r'\d+', message)
        return numbers if numbers else None
    
    return None

async def processMessage(message):
    try:
        botfeedback = handle_user_messages(message.content)
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
        #specific_channel_id = 1214734647695646754  #this is the testing one
        if message.channel.id == specific_channel_id:
            if message.author == client.user:
                return
            await processMessage(message)

    client.run(discord_token)

# def FTCScoutBot(teamNumber):
#     url = "https://api.ftcscout.org/graphql"

#     graphql_query = """
#     query GetTeamByNumber($teamNumber: Int!) {
#     teamByNumber(number: $teamNumber) {
#         name
#         sponsors
#         quickStats(season: 2023) {
#         auto {
#             rank
#             value
#         }
#         }
#     }
#     }
#     """

#     variables = {
#         "teamNumber": teamNumber  # Replace with the desired team number
#     }

#     headers = {
#         "Content-Type": "application/json"
#     }

#     response = requests.post(url, json={"query": graphql_query, "variables": variables}, headers=headers)

#     json_data = (response.json())

#     team_name = json_data['data']['teamByNumber']['name']
#     sponsors = json_data['data']['teamByNumber']['sponsors']
#     auto_rank = json_data['data']['teamByNumber']['quickStats']['auto']['rank']
#     auto_value = json_data['data']['teamByNumber']['quickStats']['auto']['value']

#     result_string = f"Team Name: {team_name}\nSponsors: {sponsors}\nAuto Rank: {auto_rank}\nAuto Value: {auto_value}"

#     return result_string
    
def FTCScoutBot(teamNumber):
    team_number = int("".join(map(str, teamNumber))) if teamNumber else None
    print(team_number)
    url = "https://api.ftcscout.org/graphql"

    graphql_query = """
    query GetTeamByNumber($teamNumber: Int!) {
        teamByNumber(number: $teamNumber) {
            name
            sponsors
            quickStats(season: 2023) {
                auto {
                    rank
                    value
                }
            }
        }
    }
    """

    variables = {
        "teamNumber": team_number  # Replace with the desired team number
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, json={"query": graphql_query, "variables": variables}, headers=headers)

    try:
        json_data = response.json()

        # Check if the 'data' key is present in the response
        if 'data' in json_data:
            team_data = json_data['data']['teamByNumber']
            team_name = team_data['name']
            sponsors = team_data['sponsors']
            auto_rank = team_data['quickStats']['auto']['rank']
            auto_value = team_data['quickStats']['auto']['value']

            result_string = f"Team Name: {team_name}\nSponsors: {sponsors}\nAuto Rank: {auto_rank}\nAuto OPR: {auto_value}"
        else:
            result_string = "No data found for the specified team number."

    except Exception as e:
        result_string = f"Error processing API response: {str(e)}"

    return result_string

if __name__ =='__main__':
    runBot()