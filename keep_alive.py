from flask import Flask
from threading import Thread
# KeepAlive function. Uses flask to keep the bot from turning off
app = Flask('')

@app.route('/')
def home():
  return "I'm still standing!"

def run():
  app.run(host='0.0.0.0',port=8080)

def keep_alive():
  t = Thread(target=run)
  t.start()