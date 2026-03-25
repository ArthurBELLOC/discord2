import asyncio
import websockets
import threading
from datab import create_channel,get_channel_by_credentials, get_channel_by_name

class ChannelManager:
    def __init__(self):
        
        self.channels = {}
        
        self.client_channel = {}

    def nvchannel(self, name, mdp, websocket):
        if name in self.channels:
            return "already_exists"
        
        existing = get_channel_by_name(name)
        if existing is not None:
            return "already_exists"

        channel_id = create_channel(name,mdp)

        self.channels[name] = {
            "id"  : channel_id,
            "mdp" : mdp,
            "clients" : {websocket}
        }
        self.client_channel[websocket] = name
        return "ok"



    def rjchannel(self, name, mdp, websocket):
        row = get_channel_by_name(name)
        if row is None:
            return "not_found"

        channel_id, channel_name, db_password = row

        if mdp != db_password:
            return "bad_password"

        if name not in self.channels:
            self.channels[name] = {
                "id": channel_id,
                "mdp": db_password,
                "clients": set()
            }

        self.channels[name]["clients"].add(websocket)
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
        if not chan["clients"]:
            self.channels.pop(chan_name, None)