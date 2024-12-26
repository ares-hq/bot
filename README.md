```
 ________  _________   ________                          
|\  _____\|\___   ___\|\   ____\                         
\ \  \__/ \|___ \  \_|\ \  \___|                         
 \ \   __\     \ \  \  \ \  \                            
  \ \  \_|      \ \  \  \ \  \____                       
   \ \__\        \ \__\  \ \_______\                     
    \|__|         \|__|   \|_______|                     
                                                         
                                                         
                                                         
 ________   ________   ________   ___  ___   _________   
|\   ____\ |\   ____\ |\   __  \ |\  \|\  \ |\___   ___\ 
\ \  \___|_\ \  \___| \ \  \|\  \\ \  \\\  \\|___ \  \_| 
 \ \_____  \\ \  \     \ \  \\\  \\ \  \\\  \    \ \  \  
  \|____|\  \\ \  \____ \ \  \\\  \\ \  \\\  \    \ \  \ 
    ____\_\  \\ \_______\\ \_______\\ \_______\    \ \__\
   |\_________\\|_______| \|_______| \|_______|     \|__|
   \|_________|                                          


```

# Versions #

## v2.0.0 ##
- **Bot is Now Verified!**
- **Bot now uses `/` commands!**
- Transferred to *FIRST* Official API
- Custom Offensive Power Ranking (OPR) Calculator
- **Revised Commands:** `/team`, `/match`, `/help`
- **New Commands:** `/favorite`
### `/team`
```js
function (/team '<number>'){
        string "Team Number"
        string "Team Name"
        string "Team Location"
        string "Team Sponsors"
        string "World Autonomous OPR"
        string "World TeleOp OPR"
        string "World End Game OPR"
        string "World Total OPR"

        return: discord-embedded-response
    }
```
### `/match`
```js
function (/match '<team-number-1> <team-number-2>'){
        string "Team 1"
        string "Team 2"
        string "Alliance Autonomous OPR"
        string "Alliance TeleOp OPR"
        string "Alliance End Game Score"
        string "Alliance Total Score"
        return: discord-embedded-response
    }
```
```js
function (/match '<team-number-1> <team-number-2> <team-number-3> <team-number-4>'){
        //Red Alliance
        string "Team 1"
        string "Team 2"
        string "Alliance Autonomous OPR"
        string "Alliance TeleOp OPR"
        string "Alliance End Game Score"
        string "Alliance Total Score"

        //Blue Alliance
        string "Team 3"
        string "Team 4"
        string "Alliance Autonomous OPR"
        string "Alliance TeleOp OPR"
        string "Alliance End Game Score"
        string "Alliance Total Score"
        return: discord-embedded-response
    }
```
### `/help`
```js
function (/info){
        string "Bot Information"
        string "Bot Version"
        string "Bot Developers"

        string PageTurn("ALL COMMANDS")
        return: discord-pages
    }
```
### `/favorite`
```js
function (/info){
        //Adds Special Server Modifiers
        ChangeBotNickname("Team #### Bot")
        return: Discord-Confirmation-Message
    }
```


## v1.5.0 ##
- Added Ability to Simulate Matches Based on Team World OPR
    - Merges Team Lookup Stats into Alliance Format\
    ```command: match <team-number-1> <team-number-2>```\
    ```returnType: plain-text```

## v1.0.0 ##
- FTCScout API Implementation
- Added Team Command
    - Teleop, Auto, and Endgame OPR
    - Team Location, Sponsors, etc.
- **Help** Command\
    ```command: help```\
    ```returnType: plain-text```


    