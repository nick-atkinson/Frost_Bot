# -*- coding: utf-8 -*-
import discord
import os
import requests
import json
import itertools
import asyncio
from replit import db
from enum import Enum
from keep_alive import keep_alive

client = discord.Client()
months = ["Földelse", "Pecunas", "Exon", "Pulchram", "Misdram", "Thaum"]
holiday = ["The Fertility Festival", "The Market Festival", "The Dance of the Stars", "The Harvest Festival", "The Festival of Endurance", "The Year's End Festival"]
days = ["Yinday", "Reiday", "Orsday", "Yekenday", "Graceday", "Blagday", "Innesday", "Visday", "Sattarday", "Greyday"]
ttime = ["Morning` :sunrise_over_mountains:", "Midday` :sunny:", "Evening` :city_sunset:", "Night` :new_moon:"]

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

def add_date(guild_id, message):
  try:
    if str(guild_id)+"date" in db:
      array = message.content.lower().split(" ")
      num = int(array[1])
      unit = array[2]

      date = db[str(guild_id)+"date"]

      if unit.startswith("d"):
        if int((date[0]+num) / 62) > 0:
          date[1] = date[1] + int((date[0]+num)/62)
        if int((date[1]) / 6) > 0:
          date[2] = date[2] + int((date[1])/6)
        date[1] = (date[1] % 6)
        
        date[0] = (date[0] + num) % 62
        if date[0] == 0:
          date[0]+=1
      elif unit.startswith("m"):
        if int((date[1]+num) / 6) > 0:
          date[2] = date[2] + int((date[1]+num)/6)
        date[1] = (date[1]+num) % 6
      elif unit.startswith("y"):
        date[2] = date[2]+num
      else:
        return "Something is wrong with your formatting. Try:\n `!adddate (+/-)Num (day/month/year)`"
      db[str(guild_id)+"date"] = date
      return "Successfully changed the date!"
    else:
      return "Please set the date first!"
  except:
    return "Something is wrong with your formatting. Try:\n `!adddate (+/-)Num (day/month/year)`"

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
  if(init_message.startswith("!addi")):
    if guild_id not in db:
      return ""
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
    db[str(guild_id)+"init"] = 0
  else:
    db[guild_id] = [obj]

def clear_initiative(guild_id):
  if guild_id in db:
    del db[guild_id]

def print_initiative(guild_id):
  if guild_id in db:
    strg = "__**Initiative**__\n"
    data = db[guild_id]
    longest = 0
    for i in data:
      if len(i[0]) > longest :
        longest = len(i[0])
    count = 0
    for i in data:
      strg = strg + "`" + i[0] + " "*(longest-len(i[0])) + " - " + str(i[1]) + " "*(2-len(str(i[1]))) + "`"
      if db[str(guild_id)+"init"] == count:
        strg = strg + " :white_check_mark:"
      strg = strg + "\n"
      count+=1
    return strg
  else:
    return "You must roll for initiative first!"

def next_init(guild_id):
  if guild_id in db:
    db[str(guild_id)+"init"] = (db[str(guild_id)+"init"] + 1) % (len(db[guild_id]))
    return print_initiative(guild_id)
  else:
    return "You must roll for initiative first!"

def back_init(guild_id):
  if guild_id in db:
    db[str(guild_id)+"init"] = (db[str(guild_id)+"init"] - 1) % (len(db[guild_id]))
    return print_initiative(guild_id)
  else:
    return "You must roll for initiative first!"

def remove_init(guild_id, message):
  if guild_id in db:
    if len(message.content.split(" ")) < 2:
      return "Entity does not exist in the initiative."
    name = message.content.split(" ")[1]
    data = db[guild_id]
    for i in data:
      if i[0].startswith(name):
          data.remove(i)
          break
    db[guild_id] = data
    return print_initiative(guild_id)
  else:
    return "You must roll for initiative first!"

def set_time(guild_id, message):
  try:
    tm = message.content.lower().split(" ")[2]
    num = 0
    if tm.startswith("1") or tm.startswith("mi"):
      num = 1
    elif tm.startswith("2") or tm.startswith("e"):
      num = 2
    elif tm.startswith("3") or tm.startswith("n"):
      num = 3
    db[str(guild_id)+"time"] = num % 4
    return get_time(guild_id)
  except:
    return "Improper command formatting. You could try:\n`!time set Morning`"

def get_time(guild_id):
  if str(guild_id)+"time" in db:
    return "`It is " + ttime[db[str(guild_id)+"time"] % 4] 
  else:
    return "You must set the time first!"

def add_time(guild_id):
  if str(guild_id)+"time" in db:
    db[str(guild_id)+"time"] = (db[str(guild_id)+"time"] + 1) % 4
    return get_time(guild_id)
  else:
    return "You must set the time first!"

def back_time(guild_id):
  if str(guild_id)+"time" in db:
    db[str(guild_id)+"time"] = (db[str(guild_id)+"time"] - 1) % 4
    return get_time(guild_id)
  else:
    return "You must set the time first!"

def eat(guild_id, display_name):
  if str(guild_id)+"time" not in db:
    return "You must set the time first!"

  pName = display_name
  obj = [pName, 0, 0, 0, 0]
  obj[db[str(guild_id)+"time"]+1] += 1

  if str(guild_id)+"eat" in db:
    array = db[str(guild_id)+"eat"]
    found = 0
    for i in array:
      if i[0].startswith(pName):
        i[db[str(guild_id)+"time"]+1] = 1
        found = 1
    if found == 0:
      array.append(obj)
    db[str(guild_id)+"eat"] = array
  else:
    db[str(guild_id)+"eat"] = [obj]
  return display_name + " has eaten!"

def nutrition(guild_id):
  if str(guild_id)+"eat" not in db:
    return "No one has eaten yet!"
    
  longest = 0
  array = db[str(guild_id)+"eat"]
  for item in array:
    if len(item[0]) > longest:
      longest = len(item[0])
  out = "***Players Who Have Eaten***\n" + " "*longest + " **Morning | Midday | Evening | Night** \n"
  for name in array:
    eaten = ["","","",""]
    count = 0
    for x in name:
      if count == 0:
        count = 1
        continue
      if x == 0:
        eaten[count-1] = "x"
      else:
        eaten[count-1] = "meat_on_bone"
      count += 1
    out = out + name[0] + " "*(longest - len(name[0])) + "   :"+ eaten[0] +":     " + "   :"+ eaten[1] +":     " + "   :"+ eaten[2] +":     " + "   :"+ eaten[3] +":     \n"
  return out 

def rest(guild_id):
  if str(guild_id)+"eat" in db:
    del db[str(guild_id)+"eat"]
  db[str(guild_id)+"time"] = 0
  return get_time(guild_id) + " `You have rested`"

def give(message):
  mesg = message.content.split(' ')
  item = ['', 0, '']
  user = ''
  msg = ['', '', '', '']
  if mesg[0] == '!give':
    msg[0] = mesg[1]
    msg[1] = mesg[2]
    msg[2] = mesg[3]
    if len(mesg) > 4:
      msg[3] = mesg[4]
  elif mesg[0].startswith('!inv'):
    msg[0] = mesg[2]
    msg[1] = mesg[3]
    msg[2] = mesg[4]
    if len(mesg) > 5:
      msg[3] = mesg[5]
    
  user = msg[0]
  if msg[1].isnumeric():
    item[1] = int(msg[1])
    item[0] = msg[2]
  elif msg[2].isnumeric():
    item[1] = int(msg[2])
    item[0] = msg[1]
  item[2] = msg[3]

  key = user + '--' + str(message.guild.id) + "inve"
  if key in db:
    found = False
    arr = db[key]
    for it in arr:
      if it[0] == item[0]:
        it[1] += item[1]
        found = True
        break
    if not found:
      arr.append(item)
    db[key] = arr
  else:
     db[key] = [item]
  ess = ''
  if item[1] > 1:
    ess = 's'
  return '***Gave item' + ess + ' to '+ user + '***'

def take(message):
  mesg = message.content.split(' ')
  item = ['', 0]
  user = ''
  msg = ['', '', '']
  if mesg[0] == '!take':
    msg[0] = mesg[1]
    msg[1] = mesg[2]
    msg[2] = mesg[3]
  elif mesg[0].startswith('!inv'):
    msg[0] = mesg[2]
    msg[1] = mesg[3]
    msg[2] = mesg[4]
    
  user = msg[0]
  if msg[1].isnumeric():
    item[1] = int(msg[1])
    item[0] = msg[2]
  elif msg[2].isnumeric():
    item[1] = int(msg[2])
    item[0] = msg[1]

  key = user + '--' + str(message.guild.id) + "inve"
  if key in db:
    found = False
    arr = db[key]
    for it in arr:
      if it[0] == item[0]:
        it[1] -= item[1]
        found = True
        if it[1] <= 0:
          arr.remove(it)
        break
    if not found:
      return "***Item could not be found***"
    db[key] = arr
  else:
     return "***This inventory does not exist***"
  ess = ''
  if item[1] > 1:
    ess = 's'
  return '***Took item' + ess + ' from '+ user + '***'

def get_inventory(message):
  msg = message.content.split(" ")
  if len(msg) < 2:
    return "**You must specify an inventory to show**\nTry: `!inv Charles`"
  user = msg[1]
  key = user + '--' + str(message.guild.id) + "inve"
  if key not in db:
    return "***This inventory does not exist***"
  arr = db[key]
  itemList = '**__' + user + "'s Inventory:__**\n"
  longest = 0
  for item in arr:
    if(longest < len(item[0])):
      longest = len(item[0])

  for item in arr:
    intLen = 2
    if len(str(item[1])) == 2:
      intLen = 1
    if len(str(item[1])) == 3:
      intLen = 0
    itemList += ('`' + str(item[1]) + ' '*intLen + '× ' + item[0] + ' '*(longest-len(item[0])) + '` ' + item[2] + '\n')
  return itemList

def clear_inventory(message):
  msg = message.content.split(" ")
  if len(msg) < 2:
    return "**You must specify an inventory to clear**\nTry: `!clear Charles`"
  user = ''
  if msg[0] == "!inv":
    user = msg[2]
  elif msg[0] == "!empty":
    user = msg[1]
  key = user + '--' + str(message.guild.id) + "inve"
  if key in db:
    del db[key]
    return "***Emptied " + user + "'s inventory***"
  else:
    return "***This inventory does not exist***"

def list_inventories(message):
  guild = str(message.guild.id)
  inventories = '**__Inventories Tracked in This Server__**\n'
  for key in db.keys():
    if (guild in key) and ("inve" in key):
      inventories += ('`'+ key[0 : key.index('--')] + '`\n')
  if not len(inventories) > 43:
    return "***No inventories tracked in this Server***"
  return inventories

def define_item(message):
  msg = message.content.split(' ')
  if (len(msg) < 2):
    return "***Please specify an item***\nUsage: `!define Sword *A simple longsword*`"
  item = msg[1]
  description = message.content[message.content.index(item)+len(item)+1:]
  key = str(message.guild.id) + "item-" + item.lower()
  if key in db.keys():
    db[key] = description
    return "***Overwrote existing item***" 
  db[key] = description
  return "***Item added***"

def identify_item(message):
  msg = message.content.split(' ')
  if (len(msg) < 2):
    return "***Please specify an item***\nUsage: `!identify Sword`"
  item = msg[1]
  key = str(message.guild.id) + "item-" + item.lower()
  inventory_key = item + '--' + str(message.guild.id) + "inve"
  if key in db.keys():
    return "**" + item + " -** " + db[key]
  if inventory_key in db.keys():
    inv = db[inventory_key]
    return_str = "**__" + item + ":__**\n"

    for thing in inv:
      temp_key = str(message.guild.id) + "item-" + thing[0].lower()
      if temp_key in db.keys():
        return_str += "**" + thing[0] + " -** " + db[temp_key] + "\n"
    if len(return_str) == (10 + len(item)):
      return "***" + item + " had no identifiable items***"
    return return_str
  return "***Item not found***"

def remove_item(message):
  msg = message.content.split(' ')
  if len(msg) < 2:
    return "***Please specify an item***\nUsage: `!remove Sword`"
  item = msg[1]
  key = str(message.guild.id) + "item-" + item.lower()
  if key in db.keys():
    del db[key]
    return "***Item deleted***"
  return "***Item not found***"

def list_items(message):
  items = "***__Items tracked in This Server__***\n"
  for key in db.keys():
    if (str(message.guild.id) in key) and ("item-" in key):
      items += ("`" + key[key.index("-")+1:] + '`\n')
  if not len(items) > 39:
    return "***No inventories tracked in this Server***"
  return items

@client.event
async def on_ready():
  print('Welcome {0.user}'.format(client))

@client.event
async def on_message(message):
  if message.author == client.user:
    return
  
  if message.content.lower().startswith('!helpme'):
    await message.channel.send('**__FROST BOT Commands:__**\n' +
     '**Initiative**\n' +
     '`!init` - Roll for initiative. Bot monitors for initiative inputs from any player in that channel.\n\tExample Responses: `Bofur 15`  or just `15`\n\tYou can change the name to whatever you like to add more than one entity to the initiative count.\n' +
     '`!endinit` - Ends the initiative count and prints out the initiative order.\n' +
     '`!addinit` - Adds an entity to the current initiative count.\n\tExample Uses: `!addinit Monster 15` or `!addinit 15`\n' +
     '`!removeinit` - Removes the given entity if they exist in the initiative.\n\tExample Use: `!removeinit Charles`\n' +
     '`!clearinit` - Clears the initiative.\n' +
     '`!i` or `!listi` - Displays the current initiative order.\n' +
     '`!nexti` - Continues to the next entity in the initiative.\n' +
     '`!lasti` - Sets the initiative to the previous entity in the order.\n\n' +
     '**Inventory**\n' +
     '`!inv [Name]` / `!inventory [Name]` - Displays the given inventory.\n' + 
     '`!give [Name] [#_Items] [Item_Name] [(Optional Emote) Item_Icon]` / `!inv add` - Gives an inventory an item.\n\tExample Use: `!give Gygax 20 Cookie :cookie:`\n' +
     '`!take [Name] [#_Items] [Item_Name]` / `!inv rem` - Removes a number of items from an inventory.\n\tExample Use: `!take Drakaras 4 Gold`\n' +
     '`!empty [Name]` / `!inv clear` - Clears a named inventory.\n\n' +
     '**Items**\n' +
     '`!identify [Item]` - Displays the identified description of an item. Will also identify the contents of entire inventories!\n' + 
     '`!define [Item] [Description]` - Adds an item that can be identified.\n\tExample Use: `!define Longsword *A simple Longsword.*`\n' +
     '`!remove [Item]` - Deletes an item and makes it no longer identifiable.\n' +
     '`!items` - Lists the identifiable items on the Server.\n\n')
    await message.channel.send(
     '\n**Date**\n' +
     '`!date` - Returns the current date in the Maetorian Empire.\n' +
     '`!setdate` - Sets the date in the Maetorian Empire.\n\tExample Uses: `!setdate 4 Exon 999` or `!setdate 31 3 1247`\n' +
     '`!adddate` - Increments the date by a given number of days, months, or years.\n\tExample Uses: `!adddate 1 month` or `!adddate 500 d`\n\n' +
     '**Time**\n' +
     '`!time` - Displays the current in-game time.\n' +
     '`!time set` - Sets the current time to `Morning|Midday|Evening|Night`\n\tExample Use: `!time set Morning`\n' +
     '`!time add` - Increments the current time.\n' +
     '`!time rem` - Decrements the current time.\n' +
     '`!eat` - You eat! Will set yourself as having eaten for that block in time.\n'+
     '`!nutrition` - Displays who has eaten that day. Resets upon `!rest`\n' +
     '`!rest` - Resets the day, as well as those who have eaten.\n\n' +
     '**Misc.**\n' +
     '`!troll` - Returns a True-Random integer using `Random.org` API\n\tExample Use: `!troll 3d6`\n' +
     '`!ping` - pong!\n' +
     '`!cat` - Displays a random image of a cat using `thecatapi.com` API\n' +
     ''
    )

  if message.content.lower().startswith('!roll 69') or message.content.lower().startswith('!troll 69'):
    await message.channel.send('*nice*')

  if message.content.lower().startswith('!cat'):
    await message.channel.send(get_cat())

  if message.content.lower() == '!help':
    await message.channel.send("Type `!helpme` for a list of commands!")

  if message.content.lower().startswith('!troll'):
    await message.channel.send(get_int(message.content))

  if message.content.lower() == '!i' or message.content.lower().startswith("!listi") and (message.content.lower() != '!listinv'):
    await message.channel.send(print_initiative(message.guild.id))
## Initiative Commands
  if message.content.lower().startswith('!addi'):
    run_initiative(message.guild.id, message.author.display_name, message.content)
    await message.channel.send(print_initiative(message.guild.id))

  if message.content.lower().startswith('!nexti'):
    await message.channel.send(next_init(message.guild.id))

  if message.content.lower().startswith('!lasti'):
    await message.channel.send(back_init(message.guild.id))

  if message.content.lower().startswith('!removei'):
    await message.channel.send(remove_init(message.guild.id, message))

  if message.content.lower().startswith('!ping'):
    await message.channel.send("pong!")
    
  if message.content.lower().startswith('!cleari'):
    clear_initiative(message.guild.id)
    await message.channel.send("***Initiative Cleared***")

  if message.content.lower().startswith('!init'):
    print(message.guild.id)
    clear_initiative(message.guild.id)
    channel = message.channel
    await channel.send('__***Roll For Initiative***__')

    def check(m):
      if m.channel == channel and not m.content.startswith('!') and not m.content.startswith('-') and not m.content.startswith('/') and m.author != client.user and not m.author.display_name.startswith("Dice"):
        run_initiative(message.guild.id, m.author.display_name,  m.content)
      return m.content.startswith('!endi') and m.channel == channel

    await client.wait_for('message', check=check)
    await channel.send(print_initiative(message.guild.id))
## Date commands
  if message.content.lower().startswith('!date'):
    await message.channel.send(get_date(message.guild.id))
  
  if message.content.lower().startswith('!setdate'):
    await message.channel.send(set_date(message.guild.id, message))

  if message.content.lower().startswith('!adddate'):
    await message.channel.send(add_date(message.guild.id, message))
## Time commands
  if message.content.lower() == '!time':
    await message.channel.send(get_time(message.guild.id))

  if message.content.lower().startswith('!time set'):
    await message.channel.send(set_time(message.guild.id, message))

  if message.content.lower().startswith('!time add'):
    await message.channel.send(add_time(message.guild.id))
    
  if message.content.lower().startswith('!time rem'):
    await message.channel.send(back_time(message.guild.id))
  
  if message.content.lower().startswith('!eat'):
    await message.channel.send(eat(message.guild.id, message.author.display_name))

  if message.content.lower().startswith('!nutrition'):
    await message.channel.send(nutrition(message.guild.id))

  if message.content.lower().startswith('!rest'):
    await message.channel.send(rest(message.guild.id))
## Inventory Commands
  if message.content.lower().startswith('!give') or message.content.lower().startswith('!inv add') or message.content.lower().startswith('!inventory add'):
    await message.channel.send(give(message))

  if message.content.lower().startswith('!take') or message.content.lower().startswith('!inv rem') or message.content.lower().startswith('!inventory rem'):
    await message.channel.send(take(message))

  if (message.content.lower().startswith('!inv') or message.content.lower().startswith('!inventory')) and not (message.content.lower().startswith('!inv add') or message.content.lower().startswith('!inventory add') or message.content.lower().startswith("!inv clear") or message.content.lower() == '!inventories'):
    await message.channel.send(get_inventory(message))

  if (message.content.lower().startswith('!empty') or message.content.lower().startswith('!inv clear')) and not (message.content.lower().startswith('!clearinit')):
    await message.channel.send(clear_inventory(message))

  if (message.content.lower().startswith('!list inv') or message.content.lower().startswith('!listinv') or message.content.lower().startswith('!inventories')):
    await message.channel.send(list_inventories(message))

  if (message.content.lower().startswith('!define')):
    await message.channel.send(define_item(message))
  
  if (message.content.lower().startswith('!identify')):
    await message.channel.send(identify_item(message))

  if (message.content.lower().startswith('!remove')):
    await message.channel.send(remove_item(message))

  if (message.content.lower().startswith('!items')):
    await message.channel.send(list_items(message))



keep_alive()
client.run(os.getenv('TOKEN'))