import discord
import os
import requests
import json
import itertools
import asyncio
from replit import db

client = discord.Client()

def get_cat():
  response = requests.get("https://api.thecatapi.com/v1/images/search")
  json_data = json.loads(response.text)
  cat_url = json_data[0]['url']
  return cat_url
  
def get_int(msg):
  msg = msg[7::].lower().strip(" ")
  if ("d" in msg):
    spt = msg.split("d")
    if len(spt[0]) > 3: spt[0] = spt[0][0:3:]
    if len(spt[1]) > 3: spt[1] = spt[1][0:3:]
    reqStr = "https://www.random.org/integers/?num=" + "".join(filter(str.isdigit, spt[0])) + "&min=1&max=" + "".join(filter(str.isdigit, spt[1])) + "&col=1&base=10&format=plain&rnd=new"
    response = requests.get(reqStr)
    out = response.text.split("\n")
    new = "True-Random Result: `["
    for i in out:
      new = new + i + ", "
    new = new[:-4] + "]`"
    return new
  else:
    return "`Improper Formatting.`"

def run_initiative(guild_id, init_message):
  pName = init_message.author.display_name
  value = init_message.content.split(" ")
  roll=""
  if len(value) >= 2:
    pName = value[0]
    roll = int(value[1])
  else:
    roll = int(value[0])

  obj = (pName, roll)
  

  if guild_id in db:
    array = db[guild_id]
    set = 0
    for i in range(len(array)):
      if array[i][1] <= obj[1]:
        array.insert(i, obj) 
        set = 1
        break
    if set == 0:
      array.append(obj)
    db[guild_id] = array
  else:
    db[guild_id] = [obj]

def clear_initiative(guild_id):
  if guild_id in db:
    del db[guild_id]

def print_initiative(guild_id):
  if guild_id in db:
    strg = "__**Initiative**__\n"
    data = db[guild_id]
    for i in data:
      strg = strg + "`" + i[0] + " - " + str(i[1]) + "`\n"
    return strg
  else:
    return "`You must roll for initiative first!`"

@client.event
async def on_ready():
  print('Welcome {0.user}'.format(client))

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  if message.content.startswith('!helpme'):
    await message.channel.send('**FROST BOT Commands:**\n' +
    '```!troll 1d20 - Returns a True-Random integer using Random.org API\n' +
     '!cat - Displays a random image of a cat using thecatapi.com API\n' +
     '!init - Roll for initiative. Bot monitors for initiative inputs from any player in that channel, which can be formatted as such:\n\tBofur 15  OR  15\nYou can change the name to whatever you like to add more than one entity to the initiative count.\n' +
     '!endinit - Ends the initiative count and prints out the initiative order.\n' +
     '!addinit - Adds an entity to the current initiative count. Formatted as either:\n\t!addinit Monster 15  OR  !addinit 15' +
     '```')

  if message.content.startswith('!roll 69') or message.content.startswith('!troll 69'):
    await message.channel.send('*nice*')

  if message.content.startswith('!cat'):
    await message.channel.send(get_cat())

  if message.content.startswith('!troll'):
    await message.channel.send(get_int(message.content))

  if message.content.startswith('!runi'):
    await message.channel.send(print_initiative(message.guild.id))

  if message.content.startswith('!addinit'):
    await message.channel.send(run_initiative(message.guild.id))

  if message.content.startswith('!init'):
    print(message.guild.id)
    clear_initiative(message.guild.id)
    channel = message.channel
    await channel.send('__***Roll For Initiative***__')

    def check(m):
      if m.channel == channel and not m.content.startswith('!') and not m.content.startswith('-') and not m.content.startswith('/') and m.author != client.user:
        run_initiative(message.guild.id, m)
      return m.content == '!endinit' and m.channel == channel

    await client.wait_for('message', check=check)
    await channel.send(print_initiative(message.guild.id))




client.run(os.getenv('TOKEN'))