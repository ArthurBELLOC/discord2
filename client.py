import asyncio
import websockets
import threading
from protocole import Protocoles
from camera import CameraManager
import json
from aiortc import RTCPeerConnection, RTCSessionDescription

SERVER_URL = "ws://localhost:9000"
protocole = Protocoles()
camera = CameraManager()
rtc_pc = None

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

            if isinstance(message, str):
                try:
                    data = json.loads(message)
                except json.JSONDecodeError:
                    data = None

                if isinstance(data, dict) and data.get("kind") == "rtc":
                    await handle_rtc_message(websocket, data)
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
                    asyncio.run_coroutine_threadsafe(websocket.send(f"__CAM_ON__:{pseudo}"),loop)
                    camera_task = asyncio.run_coroutine_threadsafe(camera.stream_to_websocket(websocket),loop)
                continue

            if text == "/cam off":
                asyncio.run_coroutine_threadsafe(websocket.send(f"__CAM_OFF__:{pseudo}"),loop)
                camera.stop_local()
                
                continue    

            if text == "/voice on":
                asyncio.run_coroutine_threadsafe(start_voice(websocket), loop)
                continue

            if text == "/voice off":
                asyncio.run_coroutine_threadsafe(stop_voice(websocket),loop)
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

async def start_voice(websocket):
    global rtc_pc

    if rtc_pc is not None:
        print("[VOICE] Appel déjà en cours.")
        return

    rtc_pc = RTCPeerConnection()

    @rtc_pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print(f"[VOICE] État WebRTC : {rtc_pc.connectionState}")

        if rtc_pc.connectionState in ["failed", "closed", "disconnected"]:
            await stop_voice()

    # Pour l'instant, pas encore de piste audio.
    # On commence juste par tester offer / answer / signaling.
    offer = await rtc_pc.createOffer()
    await rtc_pc.setLocalDescription(offer)

    msg = {
        "kind": "rtc",
        "type": "offer",
        "sdp": rtc_pc.localDescription.sdp,
        "sdpType": rtc_pc.localDescription.type,
    }

    await websocket.send(json.dumps(msg))
    print("[VOICE] Offer envoyée.")

async def stop_voice():
    global rtc_pc

    if rtc_pc is None:
        print("[VOICE] Aucun appel en cours.")
        return

    await rtc_pc.close()
    rtc_pc = None
    print("[VOICE] Appel fermé.")

async def handle_rtc_message(websocket, data):
    global rtc_pc

    msg_type = data.get("type")

    if msg_type == "offer":
        print(f"[VOICE] Offer reçue de {data.get('from', 'unknown')}")

        if rtc_pc is not None:
            print("[VOICE] Connexion déjà active, offer ignorée.")
            return

        rtc_pc = RTCPeerConnection()

        @rtc_pc.on("connectionstatechange")
        async def on_connectionstatechange():
            print(f"[VOICE] État WebRTC : {rtc_pc.connectionState}")

        offer = RTCSessionDescription(
            sdp=data["sdp"],
            type=data["sdpType"]
        )

        await rtc_pc.setRemoteDescription(offer)

        answer = await rtc_pc.createAnswer()
        await rtc_pc.setLocalDescription(answer)

        response = {
            "kind": "rtc",
            "type": "answer",
            "sdp": rtc_pc.localDescription.sdp,
            "sdpType": rtc_pc.localDescription.type,
            "from": pseudo
        }

        await websocket.send(json.dumps(response))
        print("[VOICE] Answer envoyée.")

    elif msg_type == "answer":
        print(f"[VOICE] Answer reçue de {data.get('from', 'unknown')}")

        if rtc_pc is None:
            print("[VOICE] Pas de connexion locale pour recevoir cette answer.")
            return

        answer = RTCSessionDescription(
            sdp=data["sdp"],
            type=data["sdpType"]
        )

        await rtc_pc.setRemoteDescription(answer)
        print("[VOICE] Remote description appliquée.")

    else:
        print(f"[VOICE] Message RTC inconnu : {msg_type}")

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