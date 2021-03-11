# -*- coding: utf-8 -*-
import discord
import os
import requests
import json
import itertools
import asyncio
from replit import db
from enum import Enum


client = discord.Client()
months = ["Földelse", "Pecunas", "Exon", "Pulchram", "Misdram", "Thaum"]
holiday = ["The Fertility Festival", "The Market Festival", "The Dance of the Stars", "The Harvest Festival", "The Festival of Endurance", "The Year's End Festival"]
days = ["Yinday", "Reiday", "Orsday", "Yekenday", "Graceday", "Blagday", "Innesday", "Visday", "Sattarday", "Greyday"]

def get_date(guild_id):
  if str(guild_id)+"date" in db:
    array = db[str(guild_id)+"date"]
    weekday = holiday[array[1]]
    if (array[0] < 31):
      weekday = days[(array[0]-1) % 10]
    elif (array[0] > 31):
      weekday = days[(array[0]-1) % 10 - 1]
    
    prefix = "th"
    if array[0] % 10 == 1:
      prefix = "st"
    elif array[0] % 10 == 2:
      prefix = "nd"
    elif array[0] % 10 == 3:
      prefix = "rd"

    return "The date is: " + weekday + ", the " + str(array[0]) + prefix + " of " + months[array[1]] + ", " + str(array[2])
  return "No date set yet."

def set_date(guild_id, message):
  try:
    date = message.content[9::].lower().split(" ")

    day = int(date[0]) % 62
    if day == 0:
      day = 1
    month = date[1]
    if (len("".join(filter(str.isdigit, date[1]))) > 0):
      month = (int(date[1])-1) % 6
    else:
      if (month.startswith("f")):
        month = 0
      elif (month.startswith("pe")):
        month = 1
      elif (month.startswith("e")):
        month = 2
      elif (month.startswith("pu")):
        month = 3
      elif (month.startswith("m")):
        month = 4
      elif (month.startswith("t")):
        month = 5
    year = int(date[2])
    db[str(guild_id)+"date"] = [day, month, year]
    return "Date Set."
  except:
    return "Something is wrong with your formatting. Try:\n `!setdate Day Month Year`"


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

def run_initiative(guild_id, display_name, init_message):
  if(init_message.startswith("!addinit")):
    init_message = init_message[init_message.index(" ")+1::]
  pName = display_name
  value = init_message.split(" ")
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

  if message.content.lower().startswith('!helpme'):
    await message.channel.send('**FROST BOT Commands:**\n' +
    '`!troll` - Returns a True-Random integer using Random.org API\n\tExample Use: `!troll 3d6`\n' +
     '`!cat` - Displays a random image of a cat using thecatapi.com API\n' +
     '`!init` - Roll for initiative. Bot monitors for initiative inputs from any player in that channel.\n\tExample Responses: `Bofur 15`  or just `15`\n\tYou can change the name to whatever you like to add more than one entity to the initiative count.\n' +
     '`!endinit` - Ends the initiative count and prints out the initiative order.\n' +
     '`!addinit` - Adds an entity to the current initiative count.\n\tExample Uses: `!addinit Monster 15` or `!addinit 15`\n' +
     '`!clearinit` - Clears the initiative.\n' +
     '`!i` - Displays the current initiative order.\n' +
     '')

  if message.content.lower().startswith('!roll 69') or message.content.lower().startswith('!troll 69'):
    await message.channel.send('*nice*')

  if message.content.lower().startswith('!cat'):
    await message.channel.send(get_cat())

  if message.content.lower() == '!help':
    await message.channel.send("Type !helpme for a list of commands!")

  if message.content.lower().startswith('!troll'):
    await message.channel.send(get_int(message.content))

  if message.content.lower() == '!i' or message.content.lower().startswith("!listi"):
    await message.channel.send(print_initiative(message.guild.id))

  if message.content.lower().startswith('!addinit'):
    run_initiative(message.guild.id, message.author.display_name, message.content)
    
  if message.content.lower().startswith('!clearinit'):
    clear_initiative(message.guild.id, message.author.display_name, message.content)
    await message.channel.send("***Initiative Cleared***")

  if message.content.lower().startswith('!init'):
    print(message.guild.id)
    clear_initiative(message.guild.id)
    channel = message.channel
    await channel.send('__***Roll For Initiative***__')

    def check(m):
      if m.channel == channel and not m.content.startswith('!') and not m.content.startswith('-') and not m.content.startswith('/') and m.author != client.user:
        run_initiative(message.guild.id, m.author.display_name,  m.content)
      return m.content == '!endinit' and m.channel == channel

    await client.wait_for('message', check=check)
    await channel.send(print_initiative(message.guild.id))

  if message.content.lower().startswith('!date'):
    await message.channel.send(get_date(message.guild.id))
  
  if message.content.lower().startswith('!setdate'):
    await message.channel.send(set_date(message.guild.id, message))
  




client.run(os.getenv('TOKEN'))