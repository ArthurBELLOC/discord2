import asyncio
import websockets
import threading

class ChannelManager:
    def __init__(self):
        
        self.channels = {}
        
        self.client_channel = {}

    def nvchannel(self, name, mdp, websocket):
        # Créer un nouveau channel
        if name in self.channels:
            return "already_exists"
        
        self.channels[name] = {
            "mdp": mdp,
            "clients": set([websocket])
        }
        self.client_channel[websocket] = name
        return "ok"
    
    def rjchannel(self, name, mdp, websocket):
        # Rejoindre un channel existant
        if name not in self.channels:
            return "not_found"
        
        chan = self.channels[name]
        if mdp != chan["mdp"]:
            return "bad_password"
        
        chan["clients"].add(websocket)
        self.client_channel[websocket] = name
        return "ok"
    
    def get_peers(self, websocket):
        """Retourne tous les clients du même channel que ce websocket."""
        chan_name = self.client_channel.get(websocket)
        if chan_name is None:
            return set()
        return self.channels[chan_name]["clients"]

    def leave(self, websocket):
        chan_name = self.client_channel.get(websocket)
        if not chan_name:
            return
        chan = self.channels.get(chan_name)
        if not chan:
            return
        chan["clients"].discard(websocket)
        self.client_channel.pop(websocket, None)
        # Optionnel : supprimer le channel s'il est vide
        if not chan["clients"]:
            self.channels.pop(chan_name, None)