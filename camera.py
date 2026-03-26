import cv2
import asyncio


class CameraManager:
    def __init__(self):
        self.cap = None
        self.running = False
        self.window_name = "Ma webcam"
        self.remote_window_name = "Webcam distante"

    def start_local(self):
        if self.running:
            print("[CAM] Webcam déjà active.")
            return False

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("[CAM] Impossible d'ouvrir la webcam.")
            self.cap = None
            return False

        self.running = True
        print("[CAM] Webcam activée.")
        return True

    def stop_local(self):
        was_running = self.running or self.cap is not None

        self.running = False

        if self.cap is not None:
            self.cap.release()
            self.cap = None

        try:
            cv2.destroyWindow(self.window_name)
        except cv2.error:
            pass

        if was_running:
            print("[CAM] Webcam arrêtée.")

    async def stream_to_websocket(self, websocket):
        import websockets

        if not self.running or self.cap is None:
            return

        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                await asyncio.sleep(0.05)
                continue

            cv2.imshow(self.window_name, frame)
            cv2.waitKey(1)

            frame = cv2.resize(frame, (320, 240))

            ok, buffer = cv2.imencode(
                ".jpg",
                frame,
                [cv2.IMWRITE_JPEG_QUALITY, 65]
            )
            if not ok:
                await asyncio.sleep(0.05)
                continue

            try:
                await websocket.send(buffer.tobytes())

            except websockets.exceptions.ConnectionClosedOK:
                print("[CAM] Connexion fermée proprement.")
                break

            except websockets.exceptions.ConnectionClosedError as e:
                print("[CAM] Connexion perdue :", e)
                break

            except Exception as e:
                print("[CAM] Erreur envoi vidéo :", e)
                break

            await asyncio.sleep(0.1)

        self.running = False
        self.stop_local()

    def show_remote_frame(self, data):
        import numpy as np

        arr = np.frombuffer(data, dtype=np.uint8)
        frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if frame is None:
            return

        cv2.imshow(self.remote_window_name, frame)
        cv2.waitKey(1)

    def close_remote_window(self):
        try :
            cv2.destroyWindow(self.remote_window_name)
        except cv2.error :
            pass