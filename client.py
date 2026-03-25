import asyncio
import websockets
import threading
from protocole import Protocoles

SERVER_URL = "ws://localhost:9000"
protocole = Protocoles()

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
            print("\n" + message)
            print("> ", end="", flush=True)
            if not message.startswith(f"{pseudo}:"):
               protocole.son_notif()
    except websockets.ConnectionClosed:
        print("\n[Déconnecté du serveur]")


async def send_messages(websocket):
    loop = asyncio.get_event_loop()

    def read_input():
        while True:
            text = input("> ").strip()
            if not text:
                continue

            if text == "*call" :
                protocole.appel()
                

            if text == "*stop" :
                protocole.stop()
                

            if text.startswith("/"):
                asyncio.run_coroutine_threadsafe(
                    websocket.send(text),
                    loop
                )
            else:
                # Sinon c'est du chat normal
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