import os

import discord
from dotenv import load_dotenv
import asyncio

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.my_background_task())

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    async def my_background_task(self):
        await self.wait_until_ready()
        while not self.is_closed():
            #counter += 1
            #await channel.send(counter)
            #await asyncio.sleep(60) # task runs every 60 seconds
            print("test1")
            channel = self.get_channel(CHANNEL_ID)
            voice_channel = await channel.connect()
            print("test2")
            voice_channel.play(discord.FFmpegPCMAudio(executable='ffmpeg.exe', source='sounds/idautit.mp3'))
            print("test3")
            await asyncio.sleep(60) # task runs every 60 seconds

client = MyClient()
client.run(TOKEN)