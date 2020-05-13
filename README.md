# Simple Modlogs
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](https://github.com/nerrixDE/simple-modlogs/fork) 
## About this bot
- This bot does not scales up regarding servers, it's not recommended to use it on more than 50 servers.
- There is no public version and there won't be.
- This bot is **not** a moderation-bot. It is just a mod-**log**-bot.
## How to use
- Install [discord.py](https://github.com/rapptz/discord.py).
- Put your Discord-Bot-Token into `configs.py`.
- Start the bot (`python3 bot.py`), running it in [screen](https://linux.die.net/man/1/screen) is recommended.
## Bot behaviour
- This bot has no commands, it will log `Kicks, Bans, Unbans, Mutes and Unmutes` in a channel named `mod-log` which must exist. The channel name might be changed in `configs.py`
- The bot detects mutes based on if the role `Muted` (also changeable in `configs.py`) was assigned or unassigned. It will not create a modlog-entry when the role is assigned due re-join persistance.
- The bot will log banned/muted/kicked/unmuted/unbanned bots as well as users.
- The modlog-reason is sourced from the audit-log-reason, it can be changed (or set, if none) by users having send-message-permission in the mod-log-channel.
### Example ModLog
![Reason edit](https://i.imgur.com/mNOuJbW.png)

_____________
> Notice: the modlog-case-number increases automatically based on the last modlog-entry, if first or none found, it's `1`.
