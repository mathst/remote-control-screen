import socket
import cv2
import zlib
import io
import os
import time
import threading
from PIL import Image, ImageGrab
import numpy as np
from pynput.mouse import Button, Controller
from pynput.keyboard import Controller as ConK, Key

keyboard = ConK()
mouse = Controller()

prev_img = None

class Client:
    def __init__(self, host, port_img, port_mouse, port_keyboard):
        self.host = host
        self.port_img = port_img
        self.port_mouse = port_mouse
        self.port_keyboard = port_keyboard

    def start(self):
        # Inicializando a conexão de imagem
        self.img_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.img_sock.connect((self.host, self.port_img))

        # Enviando as portas de mouse e teclado para o servidor
        self.img_sock.sendall(f'{self.port_mouse},{self.port_keyboard}'.encode())

        # Inicializando as conexões de mouse e teclado
        self.mouse_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.keyboard_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.mouse_sock.bind((self.host, self.port_mouse))
        self.keyboard_sock.bind((self.host, self.port_keyboard))

        self.mouse_sock.listen(1)
        self.keyboard_sock.listen(1)

        conn_mouse, _ = self.mouse_sock.accept()
        conn_keyboard, _ = self.keyboard_sock.accept()

        print('Conexões de mouse e teclado estabelecidas')

        threads = []
        threads.append(threading.Thread(target=self.send_screenshot, args=(self.img_sock,)))
        threads.append(threading.Thread(target=self.process_touch_event, args=(conn_mouse,)))
        threads.append(threading.Thread(target=self.process_key_event, args=(conn_keyboard,)))

        for thread in threads:
            thread.start()

    def send_screenshot(self, sock):
        global prev_img
        while True:
            # Captura a tela
            img = ImageGrab.grab().convert('L')  # Captura em grayscale

            # Se há uma imagem anterior, encontra a diferença
            if prev_img is not None:
                diff_img = cv2.absdiff(np.array(prev_img), np.array(img))

                # Ignora diferenças pequenas (menos que 30)
                _, diff_img = cv2.threshold(diff_img, 30, 255, cv2.THRESH_BINARY)

                img = Image.fromarray(diff_img)

            prev_img = img

            # Comprime a imagem
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            compressed_img = zlib.compress(img_byte_arr)

            # Envia o tipo de mensagem antes dos dados
            sock.sendall(b'image')  # Tipo de mensagem
            sock.sendall(len(compressed_img).to_bytes(4, 'big'))  # Tamanho da imagem
            sock.sendall(compressed_img)  # Dados da imagem

    def process_touch_event(self, sock):
        while True:
            # Recebe o evento de toque
            touch_event = sock.recv(1024).decode()

            # Separa o tipo de evento e a posição
            event_type, pos_str = touch_event.split(':')
            pos = tuple(map(int, pos_str.strip('()').split(',')))

            # Realiza a ação correspondente ao evento de toque
            if event_type == 'touch_down' or event_type == 'touch_move':
                mouse.position = pos
            elif event_type == 'touch_up':
                pass  # Para este exemplo, não fazemos nada no evento touch_up

    def process_key_event(self, sock):
        while True:
            # Recebe o evento de teclado
            key_event = sock.recv(1024).decode()

            # Separa o tipo de evento e a tecla
            event_type, key_str = key_event.split(':')

            # Traduz algumas teclas especiais
            if key_str in ('shift', 'ctrl', 'alt'):
                key_str = f'Key.{key_str}'
            key = eval(f'Key.{key_str}', {'Key': Key})

            # Realiza a ação correspondente ao evento de teclado
            if event_type == 'key_down':
                keyboard.press(key)
            elif event_type == 'key_up':
                keyboard.release(key)

if __name__ == "__main__":
    client = Client('10.200.0.18', 8080, 8081, 8082)
    client.start()


server:



import socket
import threading
import zlib
import io

from pynput.mouse import Button, Controller
from pynput.keyboard import Controller as ConK, Key

from PIL import Image

from kivy.core.window import Window
from kivy.app import App
from kivy.uix.widget import Widget

from threading import Thread

keyboard = ConK()
mouse = Controller()


# Endereço e porta do servidor
SERVER_HOST = '10.200.0.18'
SERVER_PORT = 8080

class MyWidget(Widget):
    def __init__(self, sock, **kwargs):
        super(MyWidget, self).__init__(**kwargs)
        self.sock = sock
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
        self._keyboard.bind(on_key_up=self._on_key_up)

    def on_touch_down(self, touch):
        print(touch)
        self.sock.sendall(f"touch_down:{touch.pos}".encode())

    def on_touch_move(self, touch):
        print(touch)
        self.sock.sendall(f"touch_move:{touch.pos}".encode())

    def on_touch_up(self, touch):
        print(touch)
        self.sock.sendall(f"touch_up:{touch.pos}".encode())
    
    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self._keyboard.unbind(on_key_up=self._on_key_up)
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        print(keycode, text, modifiers)
        self.sock.sendall(f"key_down:{keycode[1]}".encode())

    def _on_key_up(self, keyboard, keycode):
        print(keycode)
        self.sock.sendall(f"key_up:{keycode[1]}".encode())
               
class Server:
    def __init__(self, host, port_img):
        self.host = host
        self.port_img = port_img

    def start(self):
        try:
            # print('Iniciando servidor...')
            # Inicializando a conexão de imagem
            self.img_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.img_sock.connect((self.host, self.port_img))
            # Recebendo as portas de mouse e teclado do cliente
            print('Conexão de imagem estabelecida')
            try:
                ports = self.img_sock.recv(1024).decode()
                print(ports)
                port_mouse, port_keyboard = map(int, ports.split(','))
            except Exception as e:
                print('error ao enviar as portas: ',e)
                return
        except Exception as e:
            print('error: ',e)
            return
        
        # Inicializando as conexões de mouse e teclado
        self.mouse_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.keyboard_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.mouse_sock.connect((self.host, port_mouse))
        self.keyboard_sock.connect((self.host, port_keyboard))

        print('Conexões de mouse e teclado estabelecidas')

        threading.Thread(target=self.receive_image, args=(self.img_sock,)).start()
        threading.Thread(target=self.send_touch_events, args=(self.mouse_sock,)).start()
        threading.Thread(target=self.send_key_events, args=(self.keyboard_sock,)).start()

    def receive_image(self, sock):
        while True:
            data_type = sock.recv(5)  # Tipo de dados
            if data_type == b'image':
                img_len = int.from_bytes(sock.recv(4), 'big')  # Tamanho da imagem
                compressed_img = sock.recv(img_len)  # Dados da imagem

                # Descomprime a imagem
                img_byte_arr = io.BytesIO(zlib.decompress(compressed_img))
                img = Image.open(img_byte_arr)
                # Display image (you might need to update this part to fit your context)
                img.show()

    def send_touch_events(self, sock):
        self.app = App.get_running_app()
        self.app.root = MyWidget(sock)
        self.app.run()

    def send_key_events(self, sock):
        self.app = App.get_running_app()
        self.app.root = MyWidget(sock)
        self.app.run()

if __name__ == "__main__":
    server = Server(SERVER_HOST, SERVER_PORT)
    server.start()
