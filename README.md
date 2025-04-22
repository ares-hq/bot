## **ARES BOT**
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

# 🔁 Version History

---

## 🚀 v2.0.0 — Major Update

- ✅ **Bot is Now Verified!**
- ✅ **Supports Slash `/` Commands!**
- 🔁 Migrated to **FIRST Official API**
- ⚙️ Custom **Offensive Power Rating (OPR)** Calculator
- 🧠 **Updated Commands**: `/team`, `/match`, `/help`
- ⭐ **New Command**: `/favorite`

### `/team`

```js
/team <number>

// Returns:
{
  "Team Number": "...",
  "Team Name": "...",
  "Team Location": "...",
  "Team Sponsors": "...",
  "World Autonomous OPR": "...",
  "World TeleOp OPR": "...",
  "World End Game OPR": "...",
  "World Total OPR": "..."
}
```

---

### `/match`

#### 2-Team Match:
```js
/match <team-number-1> <team-number-2>

// Returns:
{
  "Team 1": "...",
  "Team 2": "...",
  "Alliance Autonomous OPR": "...",
  "Alliance TeleOp OPR": "...",
  "Alliance End Game Score": "...",
  "Alliance Total Score": "..."
}
```

#### 4-Team Match:
```js
/match <team-1> <team-2> <team-3> <team-4>

// Returns:
{
  // Red Alliance
  "Team 1": "...",
  "Team 2": "...",
  "Red Auto": "...",
  "Red TeleOp": "...",
  "Red End Game": "...",
  "Red Total": "...",

  // Blue Alliance
  "Team 3": "...",
  "Team 4": "...",
  "Blue Auto": "...",
  "Blue TeleOp": "...",
  "Blue End Game": "...",
  "Blue Total": "..."
}
```

---

### `/help`

```js
/help

// Returns:
{
  "Bot Information": "...",
  "Version": "2.0.0",
  "Developers": "...",
  "Commands": ["team", "match", "favorite"]
}
```

---

### `/favorite`

```js
/favorite

// Returns:
{
  "Effect": "Changes bot nickname in server to: Team #### Bot"
}
```

---

## 📦 v1.5.0

- ➕ Added Match Simulation Based on Team World OPR
- ➕ Merges Lookup Stats into Alliance Format

Example:
```bash
match <team-number-1> <team-number-2>
# Returns: plain-text match summary
```

---

## 🛠 v1.0.0 — Initial Release

- ✅ Implemented FTCScout API
- ✅ Added Team Command (TeleOp, Auto, Endgame, Location, Sponsors)
- ✅ Added Help Command

Example:
```bash
help
# Returns: plain-text command list
```

---

## 🧠 Helpful Notes

### Kill a Running Python Script
```bash
ps -ef | grep python3
kill <process_id>
```

### Run the App in Background
```bash
chmod +x ./monitor_and_run.sh
nohup ./monitor_and_run.sh > monitor.log 2>&1 &
```

### View Live Logs
```bash
tail -f ftcscout.log
tail -f monitor.log
```