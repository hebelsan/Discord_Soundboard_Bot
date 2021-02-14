import os

import discord
import PySimpleGUI as sg
from dotenv import load_dotenv
import asyncio
import threading
import os.path
import keyboard

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')

# map(key, file)
BINDINGS = {
  "F1": "blabla.mp3",
  "F2": "blabla2.mp3",
  "F3": "blabla3.mp3"
}

selected_sound = None
key_pressed = None


def gui():
    global selected_sound
    global key_pressed
    binding_items = []

    def set_key_pressed(key):
        global key_pressed
        key_pressed = key
    
    def set_playing_hook(key):
        global BINDINGS
        global selected_sound
        for key_name, filename in BINDINGS.items():
            if key_name == key.name:
                selected_sound = filename

    sg.theme('DarkAmber')   # Add a touch of color

    file_list_column = [
        [
            sg.Text("MP3 Sound File"),
            sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
            sg.FolderBrowse(),
        ],
        [
            sg.Listbox(
                values=[], enable_events=True, size=(45, 20), key="-FILE LIST-"
            )
        ],
    ]

    # For now will only show the name of the file that was chosen
    bindings_column = [
        [sg.Text("List of bindings")],
        [
        sg.Listbox(
                values=[], enable_events=True, size=(45, 20), key="-BINDINGS-"
            )
        ]
    ]

    # ----- Full layout -----
    layout = [
        [
            sg.Column(file_list_column),
            sg.VSeperator(),
            sg.Column(bindings_column),
        ]
    ]

    window = sg.Window("Soundboard", layout)

    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            keyboard.unhook_all()
            break

        # Folder name was filled in, make a list of files in the folder
        if event == "-FOLDER-":
            folder = values["-FOLDER-"]
            try:
                # Get list of files in folder
                file_list = os.listdir(folder)
            except:
                file_list = []

            fnames = [
                f
                for f in file_list
                if os.path.isfile(os.path.join(folder, f))
                and f.lower().endswith((".mp3"))
            ]
            window["-FILE LIST-"].update(fnames)
        
        elif event == "-FILE LIST-":  # A file was chosen from the listbox
            try:
                filename = os.path.join(
                    values["-FOLDER-"], values["-FILE LIST-"][0]
                )
                hook = keyboard.on_press(set_key_pressed)
                sg.Popup("Press any key to bind", title="test title", any_key_closes=True, button_type=5)
                keyboard.unhook(hook)
                binding_items.append(values["-FILE LIST-"][0] + " - " + "KEY:" + key_pressed.name)
                window["-BINDINGS-"].update(binding_items)
                BINDINGS[key_pressed.name] = filename
                keyboard.hook_key(key_pressed.name, set_playing_hook)
                key_pressed = None
            except:
                pass
    
    window.close()


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
        global selected_sound
        await self.wait_until_ready()
        channel = self.get_channel(int(CHANNEL_ID))
        voice_channel = await channel.connect()
        while not self.is_closed():
            await asyncio.sleep(0.1)
            if selected_sound:
                voice_channel.play(discord.FFmpegPCMAudio(executable='ffmpeg.exe', source=selected_sound))
                while voice_channel.is_playing():
                    await asyncio.sleep(0.15)
                selected_sound = None
                #await asyncio.sleep(0.05)

x = threading.Thread(target=gui)
x.start()

client = MyClient()
client.run(TOKEN)