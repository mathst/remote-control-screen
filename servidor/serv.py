from fastapi import FastAPI, WebSocket, Depends
from fastapi.responses import HTMLResponse
from fastapi.websockets import WebSocketDisconnect
from starlette.websockets import WebSocketState
from queue import Queue
from PIL import Image, ImageQt
from io import BytesIO
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import QApplication, QWidget, QLabel

import threading

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

app = FastAPI()
manager = ConnectionManager()
q_screen = Queue()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_bytes()
            print('Client:', data[:30])
            _ = data.split(b'<-------->')
            if _[0] == b'screen':
                q_screen.put((_[1], _[2]))
    except WebSocketDisconnect:
        manager.disconnect(websocket)

def qt(q):
    app = QApplication([])
    w = QWidget()
    w.setGeometry(640, 100, 800, 500)
    w.setWindowTitle('tv')

    def create_pic(w, x, y):
        def show(label):
            last_img = None
            w_width, w_height = None, None
            while True:
                box, img = q.get()
                box = eval(box.decode())
                img_io = BytesIO(img)
                img = Image.open(img_io)
                if last_img:
                    if not box: continue
                    last_img.paste(img, box)
                else:
                    last_img = img
                print(box)
                imgqt = ImageQt.ImageQt(last_img)
                qimg = QImage(imgqt)
                pix = QPixmap.fromImage(qimg)
                
                width, height = int(w.width()), int(w.height())
                if (w_width, w_height) != (width, height):
                    w_width, w_height = width, height
                    label.setFixedHeight(w_height)
                    label.setFixedWidth(w_width)
                pix = pix.scaled(int(w_width), int(w_height))
                label.setPixmap(pix)

        l1 = QLabel(w)
        l1.move(x, y)
        l1.show()
        threading.Thread(target=show, args=(l1,)).start()

    create_pic(w, 0, 0)

    # Show window
    w.show()
    # Exit the entire app
    app.exec_()

if __name__ == "__main__":
    threading.Thread(target=qt, args=(q_screen,)).start()
    import uvicorn
    uvicorn.run(app, host="10.200.0.17", port=9095)

