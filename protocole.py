import winsound
import simpleaudio as sa
import os

class Protocoles : 
    def __init__(self):
        
        base_dir = os.path.dirname(__file__)
        sound_path = os.path.join(base_dir, "sons", "NOKIA-2.wav")
        self.son = sa.WaveObject.from_wave_file(sound_path)
        self.play_obj = None


    def son_notif(self) : 
        winsound.Beep(800, 150)

    def appel(self):
        
        self.play_obj = self.son.play()

    def stop(self):
        try:
            if self.play_obj and self.play_obj.is_playing():
                self.play_obj.stop()
                self.play_obj = None
        except Exception as e:
            print("[DEBUG] Erreur dans stop():", e)
