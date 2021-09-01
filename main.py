import discord
from discord import guild
from discord import message
from discord.abc import _Overwrites
from discord.flags import Intents
from discord.permissions import PermissionOverwrite
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.utils import get, parse_time
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_choice, create_option
import asyncio
import os
import spotify
import json

import botconfig as cfg
import controllembed as embedcfg


client = commands.Bot(help_command=None, command_prefix="/", Intents=discord.Intents.all())
slash = SlashCommand(client, sync_commands=True)

channel = ""
voicechannel = ""
current_station_number = ""
current_station_name = ""
set_radio_station_channel_id = ""
set_radio_station_channel_url = ""
spotifyToken = ""
emoji = "1️⃣, 2️⃣, 3️⃣, 4️⃣, 5️⃣, 6️⃣, 7️⃣"
emoji_I = "1️⃣, 2️⃣, 3️⃣"
emoji_II = "4️⃣, 5️⃣, 6️⃣, 7️⃣"
setup = False

stations_mapping = {
    "1️⃣": "RadioBOB",
    "2️⃣": "Antenne1",
    "3️⃣": "DASDING",
    "4️⃣": "",
    "5️⃣": "",
    "6️⃣": "",
    "7️⃣": ""
}

stations = {
    "RadioBOB": "https://bob.hoerradar.de/radiobob-national-mp3-hq",
    "Antenne1": "http://stream.antenne1.de/a1stg/livestream2.mp3",
    "DASDING": "http://swr-dasding-live.cast.addradio.de/swr/dasding/live/mp3/128/stream.mp3"
}

def readjson(name):
    with open("cache.json", "r") as f:
        json_file = json.load(f)

    if (name == ""):
        return json_file
    else:
        return json_file[name]

def writejson(data):
    with open("cache.json", "w") as f:
        json.dump(data, f)


@client.event
async def on_ready():
    global setup
    print("I'm online!")
    asyncio.create_task(spotifyAuth())
    try:
        readjson("controll_channel")
        await client.change_presence(status=discord.Status.online, activity=discord.Game(""))
        setup = True
    except:
        await client.change_presence(status=discord.Status.idle, activity=discord.Game("use /setup"))

    if (setup == True):
        asyncio.create_task(songinfos_loop())


@client.event
async def on_raw_reaction_add(payload):
    global setup
    global emoji
    global emoji_I
    global emoji_II
    global voicechannel
    global current_station_number
    global current_station_name
    global set_radio_station_channel_url
    global set_radio_station_channel_id
    if (payload.member.name != client.user.name):
        if (readjson("controll_channel") != "" and readjson("controll_message") != ""):
            controll_message = readjson("controll_message")
            controll_channel = readjson("controll_channel")
            
            if (controll_message == str(payload.message_id) and controll_channel == str(payload.channel_id) and payload.emoji.name in emoji):
                channel = client.get_channel(payload.channel_id)
                message = await channel.fetch_message(payload.message_id)
                await message.remove_reaction(payload.emoji.name, payload.member)

                if (stations_mapping[payload.emoji.name] != ""):
                    try:
                        voicechannel.play(discord.FFmpegPCMAudio(stations[stations_mapping[payload.emoji.name]]))
                        current_station_name = stations_mapping[payload.emoji.name]
                        current_station_number = payload.emoji.name
                        await songinfos()
                    except:
                        try:
                            voicechannel.stop()
                            voicechannel.play(discord.FFmpegPCMAudio(stations[stations_mapping[payload.emoji.name]]))
                            current_station_name = stations_mapping[payload.emoji.name]
                            current_station_number = payload.emoji.name
                            await songinfos()
                        except:
                            delmsg = await message.channel.send("Please use first /set_voice_channel to connect the Bot to a Voice Channel")
                            await asyncio.sleep(5)
                            await delmsg.delete()

                elif (payload.emoji.name in emoji_II):
                    try:
                        if (readjson(payload.emoji.name) != ""):
                            current_station_name = "Playing custom Radio..."
                            current_station_number = payload.emoji.name
                            await songinfos()
                    
                            try:
                                voicechannel.play(discord.FFmpegPCMAudio(readjson(payload.emoji.name)))
                            except:
                                voicechannel.stop()
                                voicechannel.play(discord.FFmpegPCMAudio(readjson(payload.emoji.name)))
                    except:
                        pass


            elif (set_radio_station_channel_id.id == payload.message_id):
                if (payload.emoji.name in emoji_II):
                    try:
                        channel = client.get_channel(payload.channel_id)
                        message = await channel.fetch_message(payload.message_id)
                        await message.remove_reaction(payload.emoji.name, payload.member)
                        data = readjson("")
                        data[payload.emoji.name] = set_radio_station_channel_url
                        writejson(data)

                        await message.channel.send("Saved succesfully to bank " + payload.emoji.name)
                        set_radio_station_channel_id.id = ""
                        set_radio_station_channel_url = ""
                    except:
                        await message.channel.send("Can't save the Channel to the Bank")
                        set_radio_station_channel_id = ""
                        set_radio_station_channel_url = ""

        else:
            print("ERROR: chache.json can't read! Please check the layout")


@slash.slash(name="ping", guild_ids=cfg.guild_ids, description="Send the Bot Ping")
async def _ping(ctx):
    await ctx.send(f"Pong! ({client.latency*1000}ms)")


@slash.slash(name="setup", guild_ids=cfg.guild_ids, description="Use to setup the Bot. You must be the Owner of this Discord Server.")
async def _setup(ctx):
    global setup
    if (ctx.author.id == ctx.guild.owner_id):
        await ctx.send(f"Setting up the Bot...")
        try:
            controll_channel = await ctx.guild.create_text_channel('247_controll', Topic="Channel to Controll the 247 Bot", reason="Setup the 247 Bot", overwrites={
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=True, read_message_history=True, send_messages=False, add_reactions=True),
                ctx.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, add_reactions=True)
            })

            controll_message = await controll_channel.send(embed=embedcfg.embed)
            await controll_message.add_reaction('1️⃣')
            await controll_message.add_reaction('2️⃣')
            await controll_message.add_reaction('3️⃣')
            await controll_message.add_reaction('4️⃣')
            await controll_message.add_reaction('5️⃣')
            await controll_message.add_reaction('6️⃣')
            await controll_message.add_reaction('7️⃣')

            os.system("touch cache.json")

            data = {}
            data['controll_message'] = str(controll_message.id)
            data['controll_channel'] = str(controll_channel.id)
            writejson(data)

            asyncio.create_task(songinfos_loop())

            await ctx.channel.send("Succes! The bot is Ready to play Radio")
            await client.change_presence(status=discord.Status.online, activity=discord.Game(""))
            setup = True


        except:
            await ctx.channel.send("Faild! See in the Log for more Informations!")
    else:
        await ctx.send(f"You are not the Owner of this Discord Server. You can't use this Command!")
    

@slash.slash(name="set_voice_channel", guild_ids=cfg.guild_ids, description="Set the Voice Channel where the bot is playing. You must be the Owner of this Discord Server.", options=[
    create_option(name="voice_channel", description="Enter the Voice Channel Name", option_type=7, required=True)
])
async def _set_voice_channel(ctx, voice_channel: str):
    global setup
    if (setup == False):
        await ctx.send(f"Please use first /setup to setup the bot")
        return
    if (ctx.author.id == ctx.guild.owner_id):
        global voicechannel
        global channel
        data = readjson("")
        data['voice_channel'] = str(voice_channel.id)
        writejson(data)
        try:
            await voicechannel.disconnect()
            channel = client.get_channel(voice_channel.id)
        except:
            channel = client.get_channel(voice_channel.id)
        
        try:
            voicechannel = await channel.connect()
            await ctx.send(f"Bound the bot to " + str(voice_channel.name) + ".")
        except:
            await ctx.send(f"" + str(voice_channel.name) + " is not a valid Voice Channel")
    
    
@slash.slash(name="add_radio_station", guild_ids=cfg.guild_ids, description="Add or edit the radio station of a channel", options=[
    create_option(name="radio_station_url", description="Enter the Url to the Radio Webstream", option_type=3, required=True)
])
async def _add_radio_station(ctx, radio_station_url: str):
    global setup
    if (setup == False):
        await ctx.send("Please use first /setup to setup the bot")
        return

    global set_radio_station_channel_url
    global set_radio_station_channel_id

    if ("http" in radio_station_url):
        set_radio_station_channel_url = radio_station_url

        set_radio_station_channel_id = await ctx.send(f"Please select the Bank you want to save the Radio Station:")
        await set_radio_station_channel_id.add_reaction('4️⃣')
        await set_radio_station_channel_id.add_reaction('5️⃣')
        await set_radio_station_channel_id.add_reaction('6️⃣')
        await set_radio_station_channel_id.add_reaction('7️⃣')

    else:
        await ctx.send(f"Please enter a correct url!")


async def songinfos_loop():
    while True:
        await songinfos()
        await asyncio.sleep(30)


async def songinfos():
    global current_station_name
    global current_station_number
    global spotifyToken
    if (readjson("controll_message") != "" and readjson("controll_channel") != ""):
        controll_channel = readjson("controll_channel")
        controll_message = readjson("controll_message")


        channel = client.get_channel(int(controll_channel))
        message = await channel.fetch_message(controll_message)

        if (current_station_name == "RadioBOB"):
            try:
                data = os.popen("curl -s https://stream-service.loverad.io/v4/bob_nat?ts=1630075319870")
                data = json.load(data)
                title = data['1']['song_title'] + " - " + data['1']['artist_name']
                description = current_station_number + ": " + current_station_name
                footer = ""
            except:
                title = ""
                description = current_station_number + ": " + current_station_name
                footer = "Can't get Song Information"

        elif (current_station_name == "Antenne1"):
            try:
                data = os.popen("curl -s https://antenne1.api.radiosphere.io/channels/de897d05-97e0-477e-ae1c-7c2d4a741d1f/current-track?time=1630079993872")
                data = json.load(data)
                title = data['trackInfo']['title'] + " - " + data['trackInfo']['artistCredits']
                description = current_station_number + ": " + current_station_name
                footer = ""
            except:
                title = ""
                description = current_station_number + ": " + current_station_name
                footer = "Can't get Song Information"

        elif (current_station_name == "DASDING"):
            try:
                data = os.popen("curl -s https://www.dasding.de/~webradio/dasding-playlist-100~playerbarPlaylist_stationid-dasding_-fc792a36714c7845c21c2da2b83d3efb36eedf84.json")
                data = json.load(data)
                title = data[0]['title'] + " - " + data[0]['artist']
                description = current_station_number + ": " + current_station_name
                footer = ""
            except:
                title = ""
                description = current_station_number + ": " + current_station_name
                footer = "Can't get Song Information"
            
        elif (current_station_name == ""):
            title = 'Nothig Playing'
            description = ""
            footer = "Select a channel and listen to the Radio"

        else:
            title = ""
            description = current_station_number + ": " + current_station_name
            footer = "Station didn't support this function"

        try:
            song = title.split(' - ')[0]
            artist = title.split(' - ')[1]

            song = song.replace(' ', '%20')
            song = song.lower()

            artist = artist.replace(' ', '%20')
            artist = artist.lower()

            data = os.popen('curl -s -X "GET" "https://api.spotify.com/v1/search?q=' + song + '%20' + artist + '&type=track&limit=1" -H "Authorization: Bearer ' + spotifyToken + '"').read()        #Spotify Api: https://developer.spotify.com/console/get-search-item/

            if (data.split('"images"')[1].split('"url" : "')[1].split('",')[0] != ""):
                url = data.split('"images"')[1].split('"url" : "')[1].split('",')[0]
            else:
                url = "https://lucasserver.de/discord/icon2.png"
        except:
            url = "https://lucasserver.de/discord/icon2.png"

        embed = discord.Embed(
            title = title,
            description = description,
            color = 0x5af
        )

        embed.set_image(url=url)
        embed.set_footer(text=footer)
        
        await message.edit(embed = embed)


async def spotifyAuth():
    global spotifyToken
    while True:
        spotifyToken = spotify.getAccessToken(cfg.spotify['clientID'], cfg.spotify['clientSecret'])
        await asyncio.sleep(43200)


client.run(cfg.bot['token'])