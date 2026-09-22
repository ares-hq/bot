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

FTC team statistics and match simulation as a Discord bot. Reads the `season_<year>` table
that the [pipeline](https://github.com/ares-hq/db) writes; the two agree on table names
through [`model::tables`](https://github.com/ares-hq/model).

## Commands

### `/team <team_number>`

One team's season card: OPR by phase, overall rank, location and sponsors. A team favourited
in this server is marked with a star.

### `/match <red_alliance> [blue_alliance]`

Simulates a matchup and renders a scorecard. Each alliance is **two team numbers separated by
a space** — `/match "12345 6789" "4321 9876"`. Omit the blue alliance to score the red one on
its own, which renders an alliance card instead.

Totals follow the real scoreboard: each alliance's auto, teleop and endgame, plus the fouls
its opponent committed.

### `/favorite [team_number]`

With a team number, toggles it — the first call adds, the next removes. With no argument,
lists the server's favourites. Favourites are per-server, shared by everyone in it, and
persist across restarts.

### `/help`

Three pages of command reference and a note on how to read OPR.

## Setup

### 1. Clone

Inside the monorepo the crate is a workspace member:

```bash
git clone --recurse-submodules https://github.com/ares-hq/ares.git
cd ares
```

Standalone also works — `model` then resolves from its published branch:

```bash
git clone https://github.com/ares-hq/bot.git && cd bot
```

### 2. Create the favourites table

Once per Supabase project:

```sql
create table favorites (
  guild_id    text    not null,
  team_number integer not null,
  primary key (guild_id, team_number)
);
```

`guild_id` is text because Discord snowflakes do not round-trip through JSON integers.

### 3. Configure

Create `.env` (the monorepo keeps one at its root, shared with the pipeline):

```env
DISCORD_TOKEN=your-bot-token
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Optional
SEASON=2025            # pin the season table; defaults to the current season
DEBUG_MODE=false       # register to one guild and refuse other channels
DEV_SERVER_ID1=...     # guild for debug-mode command registration
DEV_CHANNEL_ID1=...    # channels debug mode will answer in
DEV_CHANNEL_ID2=...
```

`SEASON` exists so the bot and the pipeline can be pinned to the same year. Left unset, both
derive it from the clock, rolling over in August.

Debug mode registers commands to `DEV_SERVER_ID1` — which propagates instantly, unlike the
global registration used in production — and declines to answer outside the listed channels.

### 4. Run

```bash
cargo run --release --bin bot
```

## Design notes

- **Team reads are cached for 60 seconds.** The pipeline rewrites the season table every few
  minutes, so anything fresher than that is reused. A full `/match` is a single
  `teamNumber=in.(…)` query, not one request per team.
- **Cards are SVG.** [askama](https://github.com/djc/askama) templates in `templates/` are
  rendered by [resvg](https://github.com/linebender/resvg) into PNG, on a blocking thread so
  rasterisation never stalls the gateway. Fonts are embedded with `include_bytes!` and parsed
  once.
- **Commands are one list.** `commands::Command` drives both registration and dispatch, so a
  new command cannot be registered without also being handled.

## Deployment

Fonts and templates are compiled into the binary and TLS roots are bundled, so the image is
the binary on `scratch` — nothing else in it.

```bash
docker compose up -d bot
docker compose logs -f bot
```

`restart: unless-stopped` brings the bot back after a crash and after a daemon restart,
using docker's own backoff. Full instructions in [`deploy/README.md`](../deploy/README.md).

### Without a container runtime

```bash
chmod +x ./monitor_and_run.sh
nohup ./monitor_and_run.sh > monitor.log 2>&1 &
```

Builds, starts the bot, then checks `main` every minute — rebuilding and restarting when it
moves, and restarting the bot if it died. This needs the Rust toolchain on the host and
self-updates with `git reset --hard`, so prefer the image above where you have a choice.

## Version history

### v3.0.0

- Rewritten in Rust (was Python)
- Server favourites persist in Supabase instead of vanishing on restart
- Match and alliance cards rendered from SVG templates
- Reads the shared `season_<year>` tables through the `model` crate

### v2.0.0

- Bot verified; migrated to slash commands
- Moved to the official FIRST API with a custom OPR solver
- Added `/favorite`

### v1.5.0

- Match simulation from team OPR

### v1.0.0

- Initial release on the FTCScout API: team lookup and help
