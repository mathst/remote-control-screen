# -*- coding: utf-8 -*-
import asyncio
import time
import websockets
import threading
import queue
from PIL import Image, ImageChops, ImageGrab
import io

q_screen = queue.Queue()

def img_to_byte_arr(img):
    imgByteArr = io.BytesIO()
    img.save(imgByteArr, format='PNG')
    return imgByteArr.getvalue()

def get_changed_screen():
    im1 = ImageGrab.grab()
    imgByteArr = img_to_byte_arr(im1)
    q_screen.put(((), imgByteArr))
    
    while 1:
        print('q_screen', q_screen.qsize())
        if q_screen.qsize() > 5:
            time.sleep(1)
        im2 = ImageGrab.grab()
        diff = ImageChops.difference(im1, im2)
        box = diff.getbbox()
        if not box:
            continue
        img = im2.crop(box)
        imgByteArr = img_to_byte_arr(img)
        q_screen.put((box, imgByteArr))
        im1 = im2

threading.Thread(target=get_changed_screen, args=()).start()

async def send_screenshots(uri):
    async with websockets.connect(uri) as websocket:
        while True:
            box, img_bin = q_screen.get()
            box_bin = bytes(str(box).encode())
            await websocket.send(b'<-------->'.join([bytes('screen'.encode()), box_bin, img_bin]))
            print('sent')

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_screenshots('ws://10.200.0.17:9095/ws'))
    loop.run_forever()
