import asyncio

async def handle_client(reader, writer, conkey):
    message = conkey
    writer.write(message.encode())
    await writer.drain()

    print(f"Sent: {message}")

    try:
        while True:
            data = await reader.read(100)
            if not data:
                break
            print(f"Received: {data.decode()}")
    except asyncio.CancelledError:
        pass
    finally:
        print("Closing the connection")
        writer.close()
        await writer.wait_closed()

async def main(host, port, conkey):
    reader, writer = await asyncio.open_connection(host, port)
    await handle_client(reader, writer, conkey)

async def start_client(host, port, conkey):
    # host = '127.0.0.1'  # Change this to your server's address
    # port = 8888  # Change this to your server's port
    print('inStartClient')
    await main(host, port, conkey)

def run_event_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

def start_loop(loop):
    loop_thread = asyncio.new_event_loop()
    asyncio.set_event_loop(loop_thread)
    loop_thread.run_until_complete(start_client())

def stop_loop(loop):
    for task in asyncio.all_tasks(loop):
        task.cancel()
    loop.call_soon_threadsafe(loop.stop)







#----------------------------------------
import asyncio
import PySimpleGUI as sg
from AsyncFun import *


sg.theme('DarkAmber')

layout = [
    [sg.Push(), sg.Button('X', pad=0, key= '-CLOSE-',font='Young 15', button_color='#FF0000', border_width=2 )],
    [   
        sg.Text('IP Address'),
        sg.InputText(default_text='192.168.1.104', size=(30,30), key= '-inIP-',  justification="center" ), 
        sg.Text('Port'),
        sg.InputText(default_text='2001', size=(30,30), key= '-inPORT-', justification="center" ), 
        sg.Text('Connection Key'),
        sg.InputText(default_text='Connected', size=(30,100), key= '-inConKey-', justification="center" ), 
        sg.Button('Connect', pad=0, key= '-CONNECT-',font='Young 10 bold', button_color=('#FFFF00', '#00FA00'), border_width=2),
        sg.Button('DisConnect', pad=0, key= '-Stop-',font='Young 10 bold', button_color=('#FFFF00', '#00FA00'), border_width=2),
    
    ],

    ]


# Event loop
loop = asyncio.new_event_loop()

# Create the window
window = sg.Window(
    "Data Logger", 
    layout,
    # size=(700,500),
    # no_titlebar=True,
    element_justification='center')

# Create an event loop
while True:
    event, values = window.read(timeout=100)
    if event in [sg.WIN_CLOSED, "-Stop-"]:
        stop_loop(loop)
        break
    if event == "-CONNECT-":
        host = values['-inIP-']
        port = values['-inPORT-']
        connectionKey = values['-inConKey-']
        print(host, port, connectionKey)
        asyncio.ensure_future(start_client(host, port, connectionKey))

    # End program if user closes window or
    # presses the OK button
    if event in ["-CLOSE-", sg.WIN_CLOSED]:
        stop_loop(loop)
        break

window.close()
