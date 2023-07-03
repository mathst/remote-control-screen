import socket
import time
import threading
import json
import cv2
import lz4.frame
import numpy as np
from pynput.mouse import Listener as MouseListener, Controller
from pynput.keyboard import Listener as KeyboardListener, Key
import tkinter as tk
from PIL import Image, ImageTk
import gc
import concurrent.futures

SERVER_HOST = '10.200.0.17'
COMMAND_PORT = 3081
SCREEN_PORT = 3080
WINDOW_TITLE = "SDtv"

_mouse = Controller()

class MouseEventHandling:#empacota e envia
    def __init__(self,conn,server_screen_width, server_screen_height):
        self.conn=conn
        self.server_screen_width = server_screen_width
        self.server_screen_height = server_screen_height

    def on_move(self, x, y):#
       
        x,y=x,y
        event = {'type': 'move', 'x': x, 'y': y}
        # até aqui esta vindo as cordenadas do mouse
        json_data = json.dumps(event)
        json_data = (json_data + '\n').encode()
        client.send_comands(self.conn,json_data)
   

    def on_click(self, x, y, button, pressed):
       
        x,y=x,y
        event = {'type': 'click', 'details': {'x': x , 'y': y , 'button': str(button), 'pressed': pressed}}
        json_data = json.dumps(event)
        json_data = (json_data + '\n').encode()
        client.send_comands(self.conn,json_data)


    def on_scroll(self, x, y, dx, dy):
       
        x,y=x,y
        event = {'type': 'scroll', 'details': {'x': x, 'y': y, 'dx': dx, 'dy': dy}}
        json_data = json.dumps(event)
        json_data = (json_data + '\n').encode()
        client.send_comands(self.conn,json_data)
    


class KeyboardEventHandling:#empacota e enviaos dados do teclado
    def __init__(self,conn):
        self.conn=conn
        self.pressed_keys = set()

    def on_press(self, key):
        self.pressed_keys.add(key)
        event = {'type': 'press', 'key': str(key)}
        json_data = json.dumps(event)
        json_data = (json_data + '\n').encode()
        client.send_comands(self.conn,json_data)
      

    def on_release(self, key):
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)
            event = {'type': 'release', 'key': str(key)}
            json_data = json.dumps(event)
            json_data = (json_data + '\n').encode()
            client.send_comands(self.conn,json_data)

            
class Client:
    def __init__(self):
        self.command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.screen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True
        self.client_screen_width = 1920
        self.client_screen_height = 1080
        # self.server_screen_width = 0
        # self.server_screen_height = 0
        self.tk = tk.Tk()
        
        self.label = tk.Label(self.tk,width= self.client_screen_width,height=self.client_screen_height)
        self.label.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

        self.mouse_event_handling = MouseEventHandling(self.command_socket,self.client_screen_width, self.client_screen_height)
        self.keyboard_event_handling = KeyboardEventHandling(self.command_socket)
        

    
    def get_window_geometry(self):
        return self.tk.winfo_x(), self.tk.winfo_y(), self.tk.winfo_width(), self.tk.winfo_height()
    
    def start(self):
        self.tk.title(WINDOW_TITLE)
        self.tk.protocol("WM_DELETE_WINDOW", self.on_close)

        while self.running:
            try:
                self.command_socket.connect((SERVER_HOST, COMMAND_PORT))
                print("Conexão com o servidor de comandos estabelecida.")
                
                self.receive_screen_dimensions(self.command_socket)
                # abre janela
                time.sleep(0.1)

                self.screen_socket.connect((SERVER_HOST, SCREEN_PORT))
                print("Conexão com o servidor de tela estabelecida.")
                

                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                    executor.submit(self.receive_screen, self.screen_socket)
                    
                    executor.submit(self.captura_keyborad_e_mouse)
                    print("Threads iniciadas.")
                    # self.show_screen()

            except Exception as e:
                print(f"Erro ao estabelecer conexões: {e}")
                self.running = False
                
            except KeyboardInterrupt:
                self.running = False
                break       
        
    def captura_keyborad_e_mouse(self):
        def on_move(x, y):
            self.mouse_event_handling.on_move(x, y)
            
        def on_click(x, y, button, pressed):
            self.mouse_event_handling.on_click(x, y, button, pressed)
            
        def on_scroll(x, y, dx, dy):
            self.mouse_event_handling.on_scroll(x, y, dx, dy)

        def on_press(key):
            if hasattr(key, 'char'):
                self.keyboard_event_handling.on_press(key.char)
            else:
                self.keyboard_event_handling.on_press(str(key))

        def on_release(key):
            if hasattr(key, 'char'):
                self.keyboard_event_handling.on_release(key.char)
            else:
                self.keyboard_event_handling.on_release(str(key))

        with MouseListener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as mouse_listener, \
            KeyboardListener(on_press=on_press, on_release=on_release) as keyboard_listener:
            while self.running:
                time.sleep(0.1)

        
    def send_comands(self, conn, command):     
        try:
            if command is not None:
                conn.sendall(command)
        except BrokenPipeError:
            print("Erro ao enviar comando do mouse")
        except json.JSONDecodeError:
            print("Os dados a serem enviados não são um JSON válido")


    def receive_screen_dimensions(self, conn):
        # Receba os dados JSON
        json_data = conn.recv(1024)
        json_data = json_data.decode()
        # Converta os dados JSON em um dicionário
        data = json.loads(json_data)
        
        # Atribua os valores recebidos aos atributos correspondentes
        self.server_screen_width = data["width"]
        self.server_screen_height = data["height"]
        print("Dimensões da tela do servidor: ", self.server_screen_width, self.server_screen_height)
    

    def deserialize_screen(self, serialized_screen):
        compressed_screen = np.frombuffer(serialized_screen, dtype=np.uint8)
        print("Tela descomprimida: ")
        encoded_screen = lz4.frame.decompress(compressed_screen)
        print("Tela recebida: ")
        screen = cv2.imdecode(encoded_screen, cv2.IMREAD_COLOR)
        print("Tela decodificada: ")
        return screen

    def receive_screen(self, conn):
        while self.running:
            serialized_screen = b''
            while len(serialized_screen) < 8192:  # Supondo que você saiba o tamanho esperado dos dados
                data = conn.recv(8192)
                print(len(data))
                if not data:
                    break
                serialized_screen += data
            if not serialized_screen:
                print("Não recebeu dados do servidor")
                break
            screen = self.deserialize_screen(serialized_screen)
            print("Frame da tela recebido: ", screen)
            self.show_screen(screen)
        
    def show_screen(self, screen):
        self.screen = screen

        def update_label():
            if self.running:
                print("imagem")
                imagef = Image.fromarray(cv2.cvtColor(self.screen, cv2.COLOR_BGR2RGB))
                try:
                    self.label.image.paste(imagef)  
                except AttributeError:
                    self.label.configure(image=self.label.image)
                    self.label.image = ImageTk.PhotoImage(imagef)

            # self.tk.after(10, update_label)  # Atualizar o label independentemente do valor de self.running
        update_label()
        self.tk.mainloop()



    def on_close(self):
        self.running = False
        self.tk.destroy()

if __name__ == "__main__":

    client = Client()
    client.start()
