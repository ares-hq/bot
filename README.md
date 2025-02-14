```
                                                                       
                              AAA               RRRRRRRRRRRRRRRRR   EEEEEEEEEEEEEEEEEEEEEE   SSSSSSSSSSSSSSS 
                             A:::A              R::::::::::::::::R  E::::::::::::::::::::E SS:::::::::::::::S
                            A:::::A             R::::::RRRRRR:::::R E::::::::::::::::::::ES:::::SSSSSS::::::S
                           A:::::::A            RR:::::R     R:::::REE::::::EEEEEEEEE::::ES:::::S     SSSSSSS
                          A:::::::::A             R::::R     R:::::R  E:::::E       EEEEEES:::::S            
                         A:::::A:::::A            R::::R     R:::::R  E:::::E             S:::::S            
                        A:::::A A:::::A           R::::RRRRRR:::::R   E::::::EEEEEEEEEE    S::::SSSS         
                       A:::::A   A:::::A          R:::::::::::::RR    E:::::::::::::::E     SS::::::SSSSS    
                      A:::::A     A:::::A         R::::RRRRRR:::::R   E:::::::::::::::E       SSS::::::::SS  
                     A:::::AAAAAAAAA:::::A        R::::R     R:::::R  E::::::EEEEEEEEEE          SSSSSS::::S 
                    A:::::::::::::::::::::A       R::::R     R:::::R  E:::::E                         S:::::S
                   A:::::AAAAAAAAAAAAA:::::A      R::::R     R:::::R  E:::::E       EEEEEE            S:::::S
                  A:::::A             A:::::A   RR:::::R     R:::::REE::::::EEEEEEEE:::::ESSSSSSS     S:::::S
                 A:::::A               A:::::A  R::::::R     R:::::RE::::::::::::::::::::ES::::::SSSSSS:::::S
                A:::::A                 A:::::A R::::::R     R:::::RE::::::::::::::::::::ES:::::::::::::::SS 
               AAAAAAA                   AAAAAAARRRRRRRR     RRRRRRREEEEEEEEEEEEEEEEEEEEEE SSSSSSSSSSSSSSS   
                                                                                                   
                                                                                                   
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
        return: Discord-Embedded-Message
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
        return: Discord-Embedded-Message
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
        return: Discord-Embedded-Message
    }
```
### `/help`
```js
function (/info){
        string "Bot Information"
        string "Bot Version"
        string "Bot Developers"
        string PageTurn("ALL COMMANDS")
        return: Discord-Embedded-Pages
    }
```
### `/favorite`
```js
function (/info){
        //Adds Special Server Modifiers
        ChangeBotNickname("Team #### Bot")
        return: Discord-Embedded-Message
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


    
