# ARES Bot

```text
      ___           ___           ___           ___                                  ___                   
     /\  \         /\  \         /\__\         /\__\                  _____         /\  \                  
    /::\  \       /::\  \       /:/ _/_       /:/ _/_                /::\  \       /::\  \         ___     
   /:/\:\  \     /:/\:\__\     /:/ /\__\     /:/ /\  \              /:/\:\  \     /:/\:\  \       /\__\    
  /:/ /::\  \   /:/ /:/  /    /:/ /:/ _/_   /:/ /::\  \            /:/ /::\__\   /:/  \:\  \     /:/  /    
 /:/_/:/\:\__\ /:/_/:/__/___ /:/_/:/ /\__\ /:/_/:/\:\__\          /:/_/:/\:|__| /:/__/ \:\__\   /:/__/     
 \:\/:/  \/__/ \:\/:::::/  / \:\/:/ /:/  / \:\/:/ /:/  /          \:\/:/ /:/  / \:\  \ /:/  /  /::\  \     
  \::/__/       \::/~~/~~~~   \::/_/:/  /   \::/ /:/  /            \::/_/:/  /   \:\  /:/  /  /:/\:\  \    
   \:\  \        \:\~~\        \:\/:/  /     \/_/:/  /              \:\/:/  /     \:\/:/  /   \/__\:\  \   
    \:\__\        \:\__\        \::/  /        /:/  /                \::/  /       \::/  /         \:\__\  
     \/__/         \/__/         \/__/         \/__/                  \/__/         \/__/           \/__/  
```

FTC team stats, match predictions and live match results, right in your Discord server.

## Commands

### `/team <team_number>`

One team's season card: OPR by phase, overall rank, location and sponsors. A team favourited
in this server is marked with a star.

### `/match <red_alliance> [blue_alliance]`

Simulates a matchup and renders a scorecard. Each alliance is **two team numbers separated by
a space** — `/match "14584 6789" "4321 9876"`. Omit the blue alliance to score the red one on
its own, which renders an alliance card instead.

Totals follow the real scoreboard: each alliance's auto, teleop and endgame, plus the fouls
its opponent committed.

### `/favorite [team_number]`

With a team number, favourites it and posts a result card in that channel for every match the
team plays. Run it in another channel to move its cards there. With no argument, lists the
server's favourites and where each one posts.

### `/unfavorite <team_number>`

Removes a favourite from any channel, suggesting the server's favourites as you type.

### `/subscribe [event_code]`

Posts a result card in that channel for every match at the event. Run it in another channel to
move it. With no argument, lists the server's subscriptions. A subscription is dropped once
its event is over.

### `/unsubscribe <event_code>`

Stops an event from any channel, suggesting the server's events as you type.

Changing favourites or subscriptions needs **Manage Channels**, and the bot must be able to
send messages, embed links and attach files in the channel.

### `/help`

Three pages of command reference and a note on how to read OPR.

## Version history

### v3.1.0

- Servers can favorite several teams, and each team's match results post in the channel it was set in
- `/subscribe` posts every match result card from an event
- `/unfavorite` and `/unsubscribe` work from any channel and suggest what the server follows
- Match results post shortly after each score is official
- Team numbers are checked as you type them

### v3.0.0

- Rebuilt for speed and reliability
- Favourites are saved and no longer reset when the bot restarts
- Sharper match and alliance cards
- Team stats match the ARES website

### v2.0.0

- Bot verified; migrated to slash commands
- Moved to the official FIRST API with a custom OPR solver
- Added `/favorite`

### v1.5.0

- Match simulation from team OPR

### v1.0.0

- Initial release on the FTCScout API: team lookup and help
