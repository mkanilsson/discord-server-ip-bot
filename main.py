#!/usr/bin/python3

import os
import time
import discord
import requests
import threading
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PHONE_NUMBERS = os.getenv('PHONE_NUMBERS').split(',')
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_NUMBER = os.getenv('TWILIO_NUMBER')

print(PHONE_NUMBERS)

class MyClient(discord.Client):
    def set_sms_data(self, twilio_client, to, from_):
        self.twilio_client = twilio_client
        self.to_phone_numbers = to
        self.from_phone_number = from_

    def send_message(self, ip):
        for number in self.to_phone_numbers:
            try:
                message = self.twilio_client.messages.create(
                     body="Servern har bytat ip till "+ ip + " uppdatera i one.com",
                     to=number,
                     from_=self.from_phone_number
                 )
            except e:
                print("Failed to send sms to " + to)
                print(e)

    def get_ip(self):
        x = requests.get("https://api.ipify.org?format=json")
        return x.json()["ip"]

    def update_ip(self):
        ip = self.get_ip()

        if self.current_ip != ip:
            print("Ip has changed")
            self.current_ip = ip
            self.send_message(ip)

        return ip

    def check_ip(self):
        while True:
            self.update_ip()
            time.sleep(5*60) # sleep for 5 min

    async def on_ready(self):
        self.current_ip = self.get_ip()
        print("Bot started")
        update_ip_thread = threading.Thread(target=self.check_ip, name="Checker")
        update_ip_thread.start()

    async def on_message(self, message):
        variants = ["server ip?", "serverip?", "ip?"]
        for variant in variants:
            if message.content.startswith(variant):
                ip = self.update_ip()
                await message.channel.send("Ip adressen är `" + ip + "`")

intents = discord.Intents.default()
intents.message_content = True
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

client = MyClient(intents=intents)
client.set_sms_data(twilio_client, PHONE_NUMBERS, TWILIO_NUMBER)
client.run(TOKEN)
