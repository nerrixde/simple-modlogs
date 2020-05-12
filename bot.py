import datetime
import asyncio
import discord
import configs

client = discord.Client()

@client.event
async def on_ready():
    await client.change_presence(activity = discord.Activity(name = configs.WATCHING_STATUS, type = discord.ActivityType.watching))
    print(str(client.user) + " is started.")

@client.event
async def on_member_ban(gld, usr):
    await asyncio.sleep(0.5) # wait for audit log
    found_entry = None
    async for entry in gld.audit_logs(limit = 50, action = discord.AuditLogAction.ban, after = datetime.datetime.utcnow() - datetime.timedelta(seconds = 15), oldest_first = False):
        if entry.created_at < datetime.datetime.utcnow() - datetime.timedelta(seconds = 10):
            continue
        if entry.target.id == usr.id:
            found_entry = entry
            break
    else:
        return
    await post_modlog(guild = gld, type = "BAN", user = found_entry.user, target = usr, reason = found_entry.reason)
@client.event
async def on_member_unban(gld, usr):
    await asyncio.sleep(0.5) # wait for audit log
    found_entry = None
    async for entry in gld.audit_logs(limit = 50, action = discord.AuditLogAction.unban, after = datetime.datetime.utcnow() - datetime.timedelta(seconds = 15), oldest_first = False):
        if entry.created_at < datetime.datetime.utcnow() - datetime.timedelta(seconds = 10):
            continue
        if entry.target.id == usr.id:
            found_entry = entry
            break
    else:
        return
    await post_modlog(guild = gld, type = "UNBAN", user = found_entry.user, target = usr, reason = found_entry.reason)
@client.event
async def on_member_remove(usr):
    await asyncio.sleep(0.5) # wait for audit log
    found_entry = None
    async for entry in usr.guild.audit_logs(limit = 50, action = discord.AuditLogAction.kick, after = datetime.datetime.utcnow() - datetime.timedelta(seconds = 10), oldest_first = False): # 10 to prevent join-kick-join-leave false-positives
        if entry.created_at < datetime.datetime.utcnow() - datetime.timedelta(seconds = 10):
            continue
        if entry.target.id == usr.id:
            found_entry = entry
            break
    else:
        return
    await post_modlog(guild = usr.guild, type = "KICK", user = found_entry.user, target = usr, reason = found_entry.reason)
@client.event
async def on_member_update(before, after):
    if before.roles == after.roles:
        return
    muted_role = discord.utils.get(after.guild.roles, name = configs.MUTED_ROLE_NAME)
    if not muted_role:
        return
    if muted_role in after.roles and not muted_role in before.roles:
        if after.joined_at > (datetime.datetime.utcnow() - datetime.timedelta(seconds = 10)): # join persist mute
            return
        await asyncio.sleep(0.5) # wait for audit log
        found_entry = None
        async for entry in after.guild.audit_logs(limit = 50, action = discord.AuditLogAction.member_role_update, after = datetime.datetime.utcnow() - datetime.timedelta(seconds = 15), oldest_first = False):
            if entry.created_at < datetime.datetime.utcnow() - datetime.timedelta(seconds = 10):
                continue
            if entry.target.id == after.id and not muted_role in entry.before.roles and muted_role in entry.after.roles:
                found_entry = entry
                break
        else:
            return
        await post_modlog(guild = after.guild, type = "MUTE", user = found_entry.user, target = after, reason = found_entry.reason)
    elif muted_role not in after.roles and muted_role in before.roles:
        if after.joined_at > (datetime.datetime.utcnow() - datetime.timedelta(seconds = 10)): # join persist unmute
            return
        await asyncio.sleep(0.5) # wait for audit log
        found_entry = None
        async for entry in after.guild.audit_logs(limit = 50, action = discord.AuditLogAction.member_role_update, after = datetime.datetime.utcnow() - datetime.timedelta(seconds = 15), oldest_first = False):
            if entry.created_at < datetime.datetime.utcnow() - datetime.timedelta(seconds = 10):
                continue
            if entry.target.id == after.id and muted_role in entry.before.roles and not muted_role in entry.after.roles:
                found_entry = entry
                break
        else:
            return
        await post_modlog(guild = after.guild, type = "UNMUTE", user = found_entry.user, target = after, reason = found_entry.reason)
async def post_modlog(guild, type, user, target, reason):
    mod_log_channel = discord.utils.get(guild.text_channels, name = configs.MOD_LOG_CHANNEL_NAME)
    if not mod_log_channel:
        return
    caseid = "1"
    async for s in mod_log_channel.history(limit = 100):
        if s.author.id != client.user.id:
            continue
        if not s.embeds:
            continue
        caseid = str(int(s.embeds[0].author.name.split(" | Case ")[1]) + 1)
        break
    e = discord.Embed(color = configs.MODLOG_COLORS[type], timestamp = datetime.datetime.utcnow())
    e.set_author(name = f"{type.capitalize()} | Case {caseid}")
    e.add_field(name = "Target", value = f"<@{str(target.id)}> ({str(target)})", inline = True)
    e.add_field(name = "Moderator", value = f"<@{str(user.id)}> ({str(user)})", inline = True)
    e.add_field(name = "Reason", value = reason if reason else f"Moderator: do `.reason {caseid} <reason>`", inline = False)
    await mod_log_channel.send(embed = e)
async def edit_reason(msg):
    await msg.delete()
    pmsg = msg.content.replace(".reason ", "")
    if not " " in pmsg:
        return
    caseid = pmsg.split(" ")[0]
    if not caseid.isdigit():
        return
    new_reason = " ".join(pmsg.split(" ")[1:])
    fnd_msg = None
    async for s in msg.channel.history(limit = 500):
        if s.author.id != client.user.id:
            continue
        if not s.embeds:
            continue
        if s.embeds[0].author.name.endswith(f" | Case {caseid}"):
            fnd_msg = s
            break
    else:
        return
    fnd_em = fnd_msg.embeds[0]
    fnd_em.set_field_at(2, name = "Reason", value = new_reason, inline = False)
    await fnd_msg.edit(embed = fnd_em)

@client.event
async def on_message(msg):
    if msg.type != discord.MessageType.default or not msg.guild or msg.author.bot or not msg.content:
        return
    if msg.content.startswith(".reason ") and msg.channel.name == configs.MOD_LOG_CHANNEL_NAME:
        await edit_reason(msg)
client.run(configs.DISCORD_BOT_TOKEN)
