import asyncio
import websockets
from channels import ChannelManager
from protocole import Protocoles
from datab import create_user, get_user_by_credentials, save_message, get_histo

manager = ChannelManager()
protocole = Protocoles()
ws_to_user_id = {}


async def handler(websocket):
    try:
        async for message in websocket:

            #cam
            # frames webcam : messages binaires
            if isinstance(message, bytes):
                peers = manager.get_peers(websocket)
                if not peers:
                    continue

                to_remove = []
                for client in peers:
                    if client is websocket:
                        continue
                    try:
                        await client.send(message)
                    except:
                        to_remove.append(client)

                for c in to_remove:
                    manager.leave(c)

                continue

            # messages de contrôle caméra : messages texte spéciaux
            if isinstance(message, str) and message.startswith("__CAM_"):
                peers = manager.get_peers(websocket)
                if not peers:
                    continue

                to_remove = []
                for client in peers:
                    if client is websocket:
                        continue
                    try:
                        await client.send(message)
                    except:
                        to_remove.append(client)

                for c in to_remove:
                    manager.leave(c)

                continue

            # commandes /
            if message.startswith("/"):
                parts = message.split()
                cmd = parts[0]

                if cmd == "/create":
                    if len(parts) < 3:
                        await websocket.send("Usage: /create <nom> <mdp>")
                        continue
                    name = parts[1]
                    mdp = parts[2]
                    status = manager.nvchannel(name, mdp, websocket)
                    if status == "ok":
                        await websocket.send(f"[Serveur] Channel '{name}' créé et rejoint.")
                    elif status == "already_exists":
                        await websocket.send(f"[Serveur] Le channel '{name}' existe déjà.")
                    else:
                        await websocket.send(f"[Serveur] Erreur: {status}")

                elif cmd == "/join":
                    if len(parts) < 3:
                        await websocket.send("Usage: /join <nom> <mdp>")
                        continue
                    name = parts[1]
                    mdp = parts[2]
                    status = manager.rjchannel(name, mdp, websocket)
                    if status == "ok":
                        await websocket.send(f"[Serveur] Tu as rejoint '{name}'.")
                        channel_id = manager.channels[name]["id"]
                        history = get_histo(channel_id)
                        for username, content, created_at in history : 
                            await websocket.send(f"{content}")
                    elif status == "not_found":
                        await websocket.send(f"[Serveur] Channel '{name}' introuvable.")
                    elif status == "bad_password":
                        await websocket.send(f"[Serveur] Mauvais mot de passe.")
                    else:
                        await websocket.send(f"[Serveur] Erreur: {status}")

                elif cmd == "/leave" :
                    status = manager.leave(websocket)

                elif cmd == "/register":
                    if len(parts) < 3:
                      await websocket.send("[ERR] Usage: /register <pseudo> <mdp>")
                      continue
                    username = parts[1]
                    password = parts[2]
                    try:
                        user_id = create_user(username, password)
                        ws_to_user_id[websocket] = user_id
                        await websocket.send(f"[OK] Compte créé et connecté en tant que {username}.")
                    except Exception as e:
        
                        await websocket.send("[ERR] Ce pseudo existe déjà ou erreur DB.")
                    continue

                elif cmd == "/login":
                    if len(parts) < 3:
                        await websocket.send("[ERR] Usage: /login <pseudo> <mdp>")
                        continue
                    username = parts[1]
                    password = parts[2]
                    user_id = get_user_by_credentials(username, password)
                    if user_id is None:
                        await websocket.send("[ERR] Identifiants invalides.")
                        continue
                    ws_to_user_id[websocket] = user_id
                    await websocket.send(f"[OK] Connecté en tant que {username}.")
                    continue


                else:
                    await websocket.send("[Serveur] Commande inconnue.")

                continue

            
            peers = manager.get_peers(websocket)
            if not peers:
                continue

            # infos pour bdd
            user_id = ws_to_user_id.get(websocket)
            if user_id is None:
                await websocket.send("[Serveur] Tu dois être connecté (/register ou /login) pour parler.")
                continue
            channel_name = manager.client_channel.get(websocket)
            channel_id = manager.channels[channel_name]["id"]
            if message.startswith("__CAM_") is not True :
                save_message(channel_id, user_id, message)

            # partage
            to_remove = []
            for client in peers:
                if client is websocket:
                    continue
                try:
                    await client.send(message)
                except:
                    to_remove.append(client)

            for c in to_remove:
                manager.leave(c)

    except Exception as e:
        print("[SERVER ERROR]", e)

    finally:
        # Nettoyage à la déconnexion
        manager.leave(websocket)
        ws_to_user_id.pop(websocket, None)


async def main():
    async with websockets.serve(handler, "0.0.0.0", 9000):
        print("Serveur de chat lancé sur ws://0.0.0.0:9000")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())