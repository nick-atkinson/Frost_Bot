import discord
import os
import requests
import json
import itertools

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


  response = requests.get()

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
     '```')

  if message.content.startswith('!roll 69'):
    await message.channel.send('*nice*')

  if message.content.startswith('!cat'):
    await message.channel.send(get_cat())

  if message.content.startswith('!troll'):
    await message.channel.send(get_int(message.content))

client.run(os.getenv('TOKEN'))