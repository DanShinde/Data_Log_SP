import asyncio
import PySimpleGUI as sg
import threading

# Define the async functions
async def handle_client(reader, writer, conkey):
    message = conkey
    writer.write(message.encode())
    await writer.drain()

    print(f"Sent: {message}")

    try:
        while True:
            data = await reader.read(1024)
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
    print('Starting client...')
    await main(host, port, conkey)

# Functions to manage the event loop
def run_event_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

def start_loop(loop, host, port, conkey):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_client(host, port, conkey))

def stop_loop(loop):
    for task in asyncio.all_tasks(loop):
        task.cancel()
    print('Operation Stopped')
    loop.call_soon_threadsafe(loop.stop)

# PySimpleGUI layout
sg.theme('DarkAmber')

layout = [
    [sg.Push(), sg.Button('X', pad=0, key='-CLOSE-', font='Young 15', button_color='#FF0000', border_width=2)],
    [
        sg.Text('IP Address'),
        sg.InputText(default_text='192.168.2.21', size=(15, 1), key='-inIP-', justification="center"),
        sg.Text('Port'),
        sg.InputText(default_text='4000', size=(6, 1), key='-inPORT-', justification="center"),
        sg.Text('Connection Key'),
        sg.InputText(default_text='Connected', size=(10, 1), key='-inConKey-', justification="center"),
        sg.Button('Connect', pad=0, key='-CONNECT-', font='Young 10 bold', button_color=('#FFFF00', '#00FA00'), border_width=2),
        sg.Button('Disconnect', pad=0, key='-DISCONNECT-', font='Young 10 bold', button_color=('#FFFF00', '#00FA00'), border_width=2),
    ],
    [sg.Output(size=(80, 20))]
]

# Create the window
window = sg.Window("Async Socket Client", layout, element_justification='center')

# Create the asyncio event loop
loop = asyncio.new_event_loop()
loop_thread = threading.Thread(target=run_event_loop, args=(loop,), daemon=True)
loop_thread.start()

# Event loop for PySimpleGUI
client_task = None

while True:
    event, values = window.read(timeout=100)

    if event in [sg.WIN_CLOSED, '-CLOSE-']:
        if client_task:
            stop_loop(loop)
        break

    if event == '-CONNECT-':
        host = values['-inIP-']
        port = int(values['-inPORT-'])
        conkey = values['-inConKey-']
        window['-CONNECT-'].update(disabled=True)
        print(f"Connecting to {host}:{port} with key '{conkey}'")
        client_task = asyncio.run_coroutine_threadsafe(start_client(host, port, conkey), loop)

# sourcery skip: merge-nested-ifs
    if event == '-DISCONNECT-':
        if client_task:
            stop_loop(loop)
            client_task = None
            window['-CONNECT-'].update(disabled=False)
            print("Disconnected")

window.close()
