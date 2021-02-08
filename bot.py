import os

import discord
import PySimpleGUI as sg
from dotenv import load_dotenv
import asyncio
import threading
import os.path

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


def gui():
    global selected_sound
    sg.theme('DarkAmber')   # Add a touch of color

    file_list_column = [
        [
            sg.Text("MP3 Sound File"),
            sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
            sg.FolderBrowse(),
        ],
        [
            sg.Listbox(
                values=[], enable_events=True, size=(40, 20), key="-FILE LIST-"
            )
        ],
    ]

    # For now will only show the name of the file that was chosen
    bindings_column = [
        [sg.Text("Choose an sound file from list on left:")],
        [sg.Text(size=(40, 1), key="-TOUT-")]
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
                window["-TOUT-"].update(filename)
                selected_sound = filename
            except:
                pass
    
    window.close()

    '''
    sg.theme('DarkAmber')   # Add a touch of color
    # All the stuff inside your window.
    layout = [  [sg.Text('Some text on Row 1')],
                [sg.Text('Enter something on Row 2'), sg.InputText()],
                [sg.Button('Ok'), sg.Button('Cancel')] ]

    # Create the Window
    window = sg.Window('Window Title', layout)
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
            break
        print('You entered ', values[0])

    window.close()
    '''


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
        print("test1")
        channel = self.get_channel(int(CHANNEL_ID))
        voice_channel = await channel.connect()
        while not self.is_closed():
            print("test2")
            if selected_sound:
                voice_channel.play(discord.FFmpegPCMAudio(executable='ffmpeg.exe', source=selected_sound), after=lambda e: print('done', e))
                while voice_channel.is_playing():
                    await asyncio.sleep(0.1)
                selected_sound = None
                await asyncio.sleep(0.05)

x = threading.Thread(target=gui)
x.start()

client = MyClient()
client.run(TOKEN)