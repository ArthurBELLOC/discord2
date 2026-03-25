import winsound
import simpleaudio as sa
import os

class Protocoles : 
    def __init__(self):
        
        base_dir = os.path.dirname(__file__)
        self.sound_path = os.path.join(base_dir, "sons", "Tuturu.wav")
        self.call_path = os.path.join(base_dir, "sons", "NOKIA-2.wav")
        



    def son_notif(self) : 
        winsound.PlaySound(
            self.sound_path,
            winsound.SND_FILENAME | winsound.SND_ASYNC
        )

    def appel(self):
        winsound.PlaySound(
            self.call_path,
            winsound.SND_FILENAME | winsound.SND_ASYNC
        )

    def stop(self):
        winsound.PlaySound(None, 0)
