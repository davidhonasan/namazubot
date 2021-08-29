import os
import random
import asyncio
import datetime
import re

import discord
from discord.ext import tasks, commands
from dotenv import load_dotenv

# local
from database import Database, Alarm
from datetime_format import *
from embed import NamazuEmbed


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True

# Database
db = Database()

bot = commands.Bot(command_prefix='%', intents=intents, activity=discord.Activity(type=discord.ActivityType.watching, name="Kael cooking me. 🐟"))
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
        earliest_alarm = db.get_earliest_alarm()
        time_to_wake = earliest_alarm.alarm - datetime.datetime.now().timestamp()
        await asyncio.sleep(time_to_wake)
        await send_voyage_notification(earliest_alarm)

async def send_voyage_notification(earliest_alarm):
    message_channel = bot.get_channel(881189831189856288)
    alarm_subscribers = db.get_alarm_subscribers()
    
    mention_list = ''
    for subscriber in alarm_subscribers:
        mention_list += '<@' + subscriber.user_id + '> '
    
    embed = NamazuEmbed(title='Voyage Completed!', color=discord.Colour.green(), description=earliest_alarm.notes)
    embed.set_thumbnail(url="https://img.finalfantasyxiv.com/lds/pc/global/images/itemicon/d8/d8666795d88025ac8283db68e5df2aa337a51749.png")
    await message_channel.send(content = mention_list, embed = embed)

    db.remove_alarm(earliest_alarm.id)
    await check_voyage_tasks()

@bot.command(name='ping', help="Check bot latency")
async def ping(ctx):
    embed = NamazuEmbed(title='Pong!', description='Latency: {0}'.format(round(bot.latency*1000)))
    await ctx.reply(embed=embed, mention_author=False)

@bot.command(name='uptime', help="Check bot uptime")
async def uptime(ctx):
    start_date = styled_datetime(datetime.datetime.fromtimestamp(bot_started))
    uptime = datetime.timedelta(seconds=datetime.datetime.now().timestamp() - bot_started)
    embed = NamazuEmbed(title='Uptime', description=styled_timedelta(uptime))
    embed.set_footer(text='Start date: ' + start_date)
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

@bot.command(name='voyage', usage="<add/remove/subscribe/subscribers/*> <time> <'notes'>", help="Add timer for submersible or airship")
async def voyage_alarm(ctx, *, args=''):
    # n!voyage add
    if args[0:4] == 'add ':
        args = args[4:]
        if args.strip():
            day_re = re.compile('[0-9](?= ?d(ays?)?)')
            hr_re = re.compile('[0-2]?[0-9](?= ?h((ou)?r)?s?)')
            min_re = re.compile('[0-5]?[0-9](?= ?m(in(ute)?s?)?)')
            notes_re = re.compile('(?<=\"|\')[\s\S]+(?=\"|\')')
            day_parsed = int(day_re.search(args).group()) if day_re.search(args) else 0
            hr_parsed = int(hr_re.search(args).group()) if hr_re.search(args) else 0
            min_parsed = int(min_re.search(args).group()) if min_re.search(args) else 0
            notes_parsed = notes_re.search(args).group() if notes_re.search(args) else 'Namafel Ship'
            time_now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
            time_later = time_now + datetime.timedelta(days=day_parsed, hours=hr_parsed, minutes=min_parsed)
            db.add_alarm(time_later.timestamp(), notes_parsed)
            await ctx.reply('Alarm added: {}'.format(notes_parsed), mention_author=False)
        else:
            await ctx.reply('No arguments inputted', mention_author=False)
    
    # n!voyage remove
    elif args[0:7] == 'remove ':
        args = args[7:]
        if args.strip():
            if db.check_alarm(args):
                db.remove_alarm(args)
                await ctx.reply('Alarm removed', mention_author=False)
            else:
                await ctx.reply('Error, no alarm with id: {}'.format(args), mention_author=False)
        else:
            await ctx.reply('No arguments inputted', mention_author=False)
    
    # n!voyage subscribe
    elif args == 'subscribe':
        author = ctx.message.author
        subscribed = db.check_alarm_subscriber(author.id)

        if not subscribed:
            db.add_alarm_subscriber(author.id)
            await ctx.reply('You subscribed to the voyage alarms!', mention_author=False)
        else:
            db.remove_alarm_subscriber(author.id)
            await ctx.reply('You are no longer subscribed to the voyage alarms.', mention_author=False)

    # n!voyage subscribers
    elif args == 'subscribers':
        subscribers = db.get_alarm_subscribers()
        description = ''

        for subscriber in subscribers:
            description += '<@' + subscriber.user_id + '>\n'

        embed = NamazuEmbed(title='Alarm Subscribers', description=description if description else 'No subscribers')
        await ctx.reply(embed=embed, mention_author=False)
        
    # n!voyage
    elif args == '':
        alarms = db.get_alarms()
        current_time = datetime.datetime.now()
        embed = NamazuEmbed(title='Voyage Alarms', description='' if alarms else 'No alarms')
        for alarm in alarms:
            time_to_alarm = styled_timedelta(datetime.datetime.fromtimestamp(alarm.alarm) - current_time)
            embed.add_field(name='{0}. {1}'.format(alarm.id, alarm.notes), value=time_to_alarm, inline=False)
        embed.set_thumbnail(url="https://img.finalfantasyxiv.com/lds/pc/global/images/itemicon/d8/d8666795d88025ac8283db68e5df2aa337a51749.png")
        embed.set_footer(text='Current Time: ' + styled_datetime(current_time))
        await ctx.reply(embed=embed, mention_author=False)
        return
    else:
        await ctx.reply('Wrong parameters', mention_author=False)

    await check_voyage_tasks()

bot.run(TOKEN)