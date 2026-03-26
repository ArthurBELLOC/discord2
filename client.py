import asyncio
import websockets
import threading
from protocole import Protocoles
from camera import CameraManager

SERVER_URL = "ws://localhost:9000"
protocole = Protocoles()
camera = CameraManager()

ch = {"1", "2"}
x = None
while x not in ch:
    x = input("\n1) Nouveau Compte \n2) Se connecter")
    if x == "1" :
        pseudo = input("Ton pseudo : ").strip()
        mdp = input("\nTon mot de passe : ").strip()    
    else : 
        pseudo = input("Pseudo : ").strip()
        mdp = input("\nMot de passe : ").strip()




async def listen_messages(websocket):
    try:
        async for message in websocket:

            if isinstance(message, bytes):
                camera.show_remote_frame(message)
                continue

            if isinstance(message, str) and message.startswith("__CAM_OFF__"):
                camera.close_remote_window()
                print("\n[CAM] Webcam distante arrêtée.")
                print("> ", end="", flush=True)
                continue

            print("\n" + message)
            print("> ", end="", flush=True)
            if not message.startswith(f"{pseudo}:"):
               protocole.son_notif()
    except websockets.ConnectionClosed:
        print("\n[Déconnecté du serveur]")
    finally : 
        camera.close_remote_window()


async def send_messages(websocket):
    global camera_task
    loop = asyncio.get_event_loop()

    def read_input():
        nonlocal loop
        global camera_task

        while True:
            text = input("> ").strip()
            if not text:
                continue

            if text == "*call" :
                protocole.appel()
                

            if text == "*stop" :
                protocole.stop()

            if text == "/cam on":
                if camera.start_local() :
                    
                    camera_task = asyncio.run_coroutine_threadsafe(camera.stream_to_websocket(websocket),loop)
                continue

            if text == "/cam off":
                camera.stop_local()
                
                continue               

            if text.startswith("/"):
                asyncio.run_coroutine_threadsafe(
                    websocket.send(text),
                    loop
                )
            else:
                # Sinon msg
                asyncio.run_coroutine_threadsafe(
                    websocket.send(f"{pseudo}: {text}"),
                    loop
                )

    threading.Thread(target=read_input, daemon=True).start()

    while True:
        await asyncio.sleep(1)



async def main():
    async with websockets.connect(SERVER_URL) as websocket:
        print(f"[Connecté au serveur]")
        if x == "1":
            await websocket.send(f"/register {pseudo} {mdp}")
        else:
            await websocket.send(f"/login {pseudo} {mdp}")

        resp = await websocket.recv()
        print(resp)
        if resp.startswith("[ERR]"):
            print("Impossible de continuer (login/register raté).")
            return
        
        await asyncio.gather(
            listen_messages(websocket),
            send_messages(websocket)
        )

if __name__ == "__main__":
    asyncio.run(main())