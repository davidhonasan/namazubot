import os
import random
from database import Database, Alarm
import asyncio
import datetime
import re

from embed import NamazuEmbed
import discord
from discord.ext import tasks, commands
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.members = True

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Database
db = Database()

bot = commands.Bot(command_prefix='n!', intents=intents, activity=discord.Activity(type=discord.ActivityType.watching, name="Kael cooking me. 🐟"))
bot_started = 0

@bot.event
async def on_ready():
    global bot_started
    bot_started = datetime.datetime.now().timestamp()
    now = bot_started
    print(f'{bot.user.name} has connected to Discord!')
    await check_voyage_tasks()

async def check_voyage_tasks():
    if db.get_alarms():
        time_to_wake = db.get_earliest_alarm().alarm - datetime.datetime.now().timestamp()
        await asyncio.sleep(time_to_wake)
        await send_voyage_notification()

async def send_voyage_notification():
    message_channel = bot.get_channel(828698925426278440)
    alarm_subscribers = db.get_alarm_subscribers()
    earliest_alarm = db.get_earliest_alarm()
    mention_list = ''
    for userid in alarm_subscribers:
        mention_list += '<@' + userid[0] + '> '
    
    embed = NamazuEmbed(title='Voyage Completed!', color=discord.Colour.green(), description=earliest_alarm.notes)
    embed.set_thumbnail(url="https://img.finalfantasyxiv.com/lds/pc/global/images/itemicon/d8/d8666795d88025ac8283db68e5df2aa337a51749.png")
    await message_channel.send(content = mention_list, embed = embed)

    db.remove_alarm(earliest_alarm.id)
    await check_voyage_tasks()

@bot.command(name='ping', help="Check bot latency")
async def ping(ctx):
    embed = NamazuEmbed(title='Pong!', description=round(bot.latency*1000))
    await ctx.reply(embed=embed, mention_author=False)

@bot.command(name='uptime', help="Check bot uptime")
async def uptime(ctx):
    uptime = str(datetime.timedelta(seconds=datetime.datetime.now().timestamp() - bot_started))
    embed = NamazuEmbed(title='Bot Uptime', description=uptime)
    embed.add_field(name='Start date', value=str(datetime.datetime.fromtimestamp(round(bot_started))))
    await ctx.reply(embed=embed, mention_author=False)

@bot.command(name='roll', help="Pick out one of a member of certain role.")
async def roll(ctx, role: discord.Role = None):
    if not role:
        await ctx.send('Please add role into argument')
        return
    if role.members:
        winner = random.choice(role.members)
        await ctx.send("Out of {} participant(s), I choose you {} as the winner. Congratulations! 🎉".format(len(role.members), winner.mention))
    else:
        await ctx.send("Nobody has the role {}".format(role.mention))        

@roll.error
async def roll_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.RoleNotFound):
        await ctx.send('There is no {} role.', error)

@bot.command(name='voyage_subscribe', help="Subscribe to voyage alarm")
async def subscribe_voyage_alarm(ctx):
    author = ctx.message.author
    subscribed = db.check_alarm_subscriber(author.id)

    if not subscribed:
        db.add_alarm_subscriber(author.id)
        await ctx.reply('You are subscribed to the alarm!', mention_author=False)
    else:
        db.remove_alarm_subscriber(author.id)
        await ctx.reply('You are no longer subscribed', mention_author=False)

@bot.command(name='voyage_subscribers', help="List of Voyage Subscribers")
async def voyage_subscribers_list(ctx):
    subs_list = db.get_alarm_subscribers()
    await ctx.send(subs_list)

@bot.command(name='voyage', help="Add timer for submersible or airship")
async def voyage_alarm(ctx, actions = None, *args):
    # n!voyage add
    if actions == 'add':
        if args:
            args = ' '.join(args)
            day_re = re.compile('[0-9](?= ?d(ays?)?)')
            hr_re = re.compile('[0-2]?[0-9](?= ?h((ou)?r)?s?)')
            min_re = re.compile('[0-5]?[0-9](?= ?m(in(ute)?s?)?)')
            day_parsed = int(day_re.search(args).group()) if day_re.search(args) else 0
            hr_parsed = int(hr_re.search(args).group()) if hr_re.search(args) else 0
            min_parsed = int(min_re.search(args).group()) if min_re.search(args) else 0
            time_now = datetime.datetime.now(datetime.timezone.utc).replace(second=0, microsecond=0)
            time_later = time_now + datetime.timedelta(days=day_parsed, hours=hr_parsed, minutes=min_parsed)
            db.add_alarm(time_later.timestamp())
            await ctx.reply('Alarm added', mention_author=False)
        else:
            await ctx.reply('No arguments inputted', mention_author=False)
    
    # n!voyage remove
    elif actions == 'remove':
        if args:
            args = ' '.join(args)
            if db.check_alarm(args):
                db.remove_alarm(args)
                await ctx.reply('Alarm removed', mention_author=False)
            else:
                await ctx.reply('Error, no alarm with id: {}'.format(args), mention_author=False)
        else:
            await ctx.reply('No arguments inputted', mention_author=False)
    
    # n!voyage
    else:
        alarms = db.get_alarms()
        embed = NamazuEmbed(title='Voyage Alarms')
        for alarm in alarms:
            embed.add_field(name=datetime.datetime.fromtimestamp(alarm.alarm), value=alarm.notes, inline=False)
        embed.set_thumbnail(url="https://img.finalfantasyxiv.com/lds/pc/global/images/itemicon/d8/d8666795d88025ac8283db68e5df2aa337a51749.png")
        await ctx.reply(embed=embed, mention_author=False)
        return
    
    await check_voyage_tasks()

bot.run(TOKEN)