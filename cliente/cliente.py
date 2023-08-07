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

import socket
import threading
import time
import concurrent.futures
import zlib
import select
from PIL import ImageGrab

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import mainthread
import time

SERVER_HOST ="10.200.0.15"  # Defina o IP do servidor aqui
SERVER_PORT = 6651       # Defina a porta do servidor aqui
PROCESSING_SLACK = 0.1
server_address = ('10.200.0.15', 6651)

class DataCompressor:
    @staticmethod
    def compress(data):
        return zlib.compress(data)

    @staticmethod
    def decompress(data):
        return zlib.decompress(data)

class MouseCursorController(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mouse = MouseController()
        self.keyboard = KeyboardController()

    def set_cursor_pos(self, x, y):
        self.mouse.position = (x, y)

    def mouse_event(self, button, action):
        if action == "down":
            self.mouse.press(button)
        elif action == "up":
            self.mouse.release(button)

    def on_touch_down(self, touch):
        self.set_cursor_pos(touch.x, touch.y)
        self.mouse_event(MouseController().Button.left, "down")

    def on_touch_up(self, touch):
        self.mouse_event(MouseController().Button.left, "up")

# Handlers para cada tipo de conexão
class DesktopHandler:
    def __init__(self, client_socket):
        self.client_socket = client_socket
        self.running = True

    def run(self):
        while self.running:
            try:
                data = self.client_socket.recv(1024).decode("utf-8")
                if not data:
                    print("Conexão fechada pelo servidor.")
                    break

                # Lógica para lidar com as mensagens do Desktop
                # ...

            except Exception as e:
                print("Ocorreu um erro ao receber dados do Desktop:", e)
                break
    
    # Helper functions for capturing the screen and sending image data
        
    # def get_screen_as_bytes():
    #     screen = ImageGrab.grab()
    #     screen_bytes = screen.tobytes()
    #     return screen_bytes

    # def compress_data(data):
    #     return DataCompressor.compress(data)

    # while True:
    #     try:
    #         data = self.receiver.receive()
    #         if not data:
    #             break

    #         # Process received desktop screen commands
    #         # ...

    #         # Capture the screen and compress image data
    #         screen_data = get_screen_as_bytes()
    #         compressed_data = compress_data(screen_data)

    #         # Send compressed image data to the server
    #         self.sender.send(compressed_data)
    #     except Exception as e:
    #         print(f"Error handling desktop screen: {e}")
    #         break
    
    def stop(self):
        self.running = False

class KeyboardHandler:
    def __init__(self, client_socket):
        self.client_socket = client_socket
        self.running = True

    def run(self):
        while self.running:
            try:
                data = self.client_socket.recv(1024).decode("utf-8")
                if not data:
                    print("Conexão fechada pelo servidor.")
                    break

                # Lógica para lidar com as mensagens do Keyboard
                # ...

            except Exception as e:
                print("Ocorreu um erro ao receber dados do Keyboard:", e)
                break

    def stop(self):
        self.running = False

class FileShareHandler:
    def __init__(self, client_socket):
        self.client_socket = client_socket
        self.running = True

    def run(self):
        while self.running:
            try:
                data = self.client_socket.recv(1024).decode("utf-8")
                if not data:
                    print("Conexão fechada pelo servidor.")
                    break

                # Lógica para lidar com as mensagens de FileShare
                # ...

            except Exception as e:
                print("Ocorreu um erro ao receber dados do FileShare:", e)
                break

    def stop(self):
        self.running = False
    
        
class MainHandle():
    def __init__(self, client_socke):
        super().__init__()
        self.client_socket = client_socke
        self.timeout = 0
        self.running = True
        cursor_controller = MouseCursorController()
        self.handlers = [
            '<|PING|>',
            '<|ACCESSING|>',
            '<|IDEXISTS!REQUESTPASSWORD|>',
            '<|IDNOTEXISTS|>',
            '<|ACCESSDENIED|>',
            '<|ACCESSBUSY|>',
            '<|ACCESSBUSY|>',
            '<|DISCONNECTED|>'
        ]
    def run(self):    
        while self.running:
            try:
                self.timeout = 0

                buffer = self.client_socket.recv(1024).decode("utf-8")
                buffertpm = buffer
                if buffertpm.startswith('<|ID|>'):
                    datalist= buffer.split('<|>')
                    # Remove os caracteres '<', '|' e '>'
                    id_ = datalist[0].replace('<|ID|>', '').replace('-', '')
                    password_ = datalist[1].replace('<|END|>', '').replace('-', '')
                    
                    print("ID:", id_)
                    print("Password:", password_)
                
                elif buffertpm in self.handlers:
                    self.handle_message(buffertpm)
                    print(buffertpm)
                   
                elif buffertpm.startswith('<|SETPING|>'):
                    self.set_ping(buffertpm)
                    
                elif buffertpm.startswith('<|RESOLUTION|>'):
                    pass 
                       
                elif buffertpm.startswith('<|SETMOUSEPOS|>'):
                    pass
                        
                elif buffertpm.startswith('<|SETMOUSELEFTCLICKDOWN|>'):
                    pass
                    
                elif buffertpm.startswith('<|SETMOUSELEFTCLICKUP|>'):
                    pass 
                       
                elif buffertpm.startswith('<|SETMOUSERIGHTCLICKDOWN|>'):
                    pass
                        
                elif buffertpm.startswith('<|SETMOUSERIGHTCLICKUP|>'):
                    pass
                    
                elif buffertpm.startswith('<|SETMOUSEMIDDLEDOWN|>'):
                    pass
                    
                elif buffertpm.startswith('<|SETMOUSEMIDDLEUP|>'):
                    pass 
                       
                elif buffertpm.startswith('<|WHEELMOUSE|>'):
                    pass
                        
                elif buffertpm.startswith('<|CLIPBOARD|>'):
                    pass
                        
                else:
                    print("No matching action for data:", buffer)
                        
       
            except Exception as e:
                print("Ocorreu um erro:", e)
                break
                
    def handle_message(self, data):
        match data:
            case '<|PING|>':
                self.handle_ping(data)
            case '<|ACCESSING|>':
                self.handle_warns_access_and_remove_wallpaper(data)
            case '<|IDEXISTS!REQUESTPASSWORD|>':
                self.handle_id_exists_request_password(data)
            case '<|IDNOTEXISTS|>':
                self.handle_id_not_exists(data)
            case '<|ACCESSDENIED|>':
                self.handle_wrong_password(data)
            case '<|ACCESSBUSY|>':
                self.handle_pc_busy(data)
            case '<|ACCESSGRANTED|>':
                self.handle_access_granted(data)
            case '<|DISCONNECTED|>':
                self.handle_lost_connection_to_pc(data)                         
         
    def handle_ping(self, data):
        self.client_socket.send(b'<|PONG|>')
        
    def set_ping(self, data):
        print("aaaaaaaaaaaaaa")
        datalist= data.split('<|>')
        # Remove os caracteres '<', '|' e '>'
        id_ = datalist[0].replace('<|ID|>', '').replace('-', '')
        password_ = datalist[1].replace('<|END|>', '').replace('-', '')
   

    def handle_warns_access_and_remove_wallpaper(self, data):
        # Lógica para lidar com o aviso de acesso e remoção do papel de parede
        print("acesso permitido")
        pass

    def handle_id_exists_request_password(self, data):
        # Lógica para lidar com a solicitação de senha quando o ID existe
        pass

    def handle_id_not_exists(self, data):
        # Lógica para lidar com o caso de ID inexistente
        pass

    def handle_wrong_password(self, data):
        # Lógica para lidar com a senha incorreta
        pass

    def handle_pc_busy(self, data):
        # Lógica para lidar com o caso de PC ocupado
        pass

    def handle_access_granted(self, data):
        # Lógica para lidar com o acesso concedido
        pass

    def handle_lost_connection_to_pc(self, data):
        # Lógica para lidar com a perda de conexão com o PC
        pass
    
    # Função para alterar a resolução
    def set_resolution(self,data):
        datalist= data.split('<|>')
        # Remove os caracteres '<', '|' e '>'
        width = datalist[0].replace('<|ID|>', '').replace('-', '')
        height = datalist[1].replace('<|END|>', '').replace('-', '')
        # Implemente aqui a lógica para alterar a resolução
        
        print(f"Resolução alterada para {width}x{height}")

    # Função para definir a posição do mouse
    def set_mouse_pos(self,data):
        datalist= data.split('<|>')
        # Remove os caracteres '<', '|' e '>'
        width = datalist[0].replace('<|ID|>', '').replace('-', '')
        height = datalist[1].replace('<|END|>', '').replace('-', '')
        
        # cursor_controller.set_cursor_pos(200, 200)
        
        # Implemente aqui a lógica para definir a posição do mouse
        print(f"Mouse posicionado em ({x}, {y})")

    # Funções para cliques do mouse
    def set_mouse_left_click_down(self,data):
        datalist= data.split('<|>')
        # Remove os caracteres '<', '|' e '>'
        width = datalist[0].replace('<|ID|>', '').replace('-', '')
        height = datalist[1].replace('<|END|>', '').replace('-', '')
        
        # Implemente aqui a lógica para clicar o botão esquerdo do mouse
        print("Botão esquerdo do mouse pressionado")

    def set_mouse_left_click_up(self,data):
        datalist= data.split('<|>')
        # Remove os caracteres '<', '|' e '>'
        width = datalist[0].replace('<|ID|>', '').replace('-', '')
        height = datalist[1].replace('<|END|>', '').replace('-', '')

        # cursor_controller.mouse_event(MouseController().Button.left, "up")
        
        # Implemente aqui a lógica para liberar o botão esquerdo do mouse
        print("Botão esquerdo do mouse liberado")

    def set_mouse_right_click_down(self,data):
        datalist= data.split('<|>')
        # Remove os caracteres '<', '|' e '>'
        width = datalist[0].replace('<|ID|>', '').replace('-', '')
        height = datalist[1].replace('<|END|>', '').replace('-', '')
        
        # cursor_controller.mouse_event(MouseController().Button.left, "down")
        
        # Implemente aqui a lógica para clicar o botão direito do mouse
        print("Botão direito do mouse pressionado")

    def set_mouse_right_click_up(self,data):
        datalist= data.split('<|>')
        # Remove os caracteres '<', '|' e '>'
        width = datalist[0].replace('<|ID|>', '').replace('-', '')
        height = datalist[1].replace('<|END|>', '').replace('-', '')
        
        # Implemente aqui a lógica para liberar o botão direito do mouse
        print("Botão direito do mouse liberado")

    def set_mouse_middle_down(self,data):
        datalist= data.split('<|>')
        # Remove os caracteres '<', '|' e '>'
        width = datalist[0].replace('<|ID|>', '').replace('-', '')
        height = datalist[1].replace('<|END|>', '').replace('-', '')
        
        # Implemente aqui a lógica para clicar o botão central do mouse
        print("Botão central do mouse pressionado")

    def set_mouse_middle_up(self,data):
        datalist= data.split('<|>')
        # Remove os caracteres '<', '|' e '>'
        width = datalist[0].replace('<|ID|>', '').replace('-', '')
        height = datalist[1].replace('<|END|>', '').replace('-', '')
        
        # Implemente aqui a lógica para liberar o botão central do mouse
        print("Botão central do mouse liberado")

    # Função para rolar o mouse
    def wheel_mouse(self,data):
        datalist= data.split('<|>')
        # Remove os caracteres '<', '|' e '>'
        delta = datalist[0].replace('<|ID|>', '').replace('-', '')
        height = datalist[1].replace('<|END|>', '').replace('-', '')
        
        # Implemente aqui a lógica para rolar o mouse
        if delta > 0:
            print("Mouse rolado para cima")
        elif delta < 0:
            print("Mouse rolado para baixo")
        
        # Exemplo de uso para a função wheel_mouse
        # time.sleep(2)
        # cursor_controller.wheel_mouse(1)  # Rola para cima
        # time.sleep(1)
        # cursor_controller.wheel_mouse(-1)  # Rola para baixo

    # Função para manipular a área de transferência
    def clipboard(self,data):
        datalist= data.split('<|>')
        # Remove os caracteres '<', '|' e '>'
        width = datalist[0].replace('<|ID|>', '').replace('-', '')
        height = datalist[1].replace('<|END|>', '').replace('-', '')
        # Implemente aqui a lógica para alterar a resolução
        
        # Implemente aqui a lógica para manipular a área de transferência
        print(f"Texto '{text}' copiado para a área de transferência")
        
class ThreadManager:
    def __init__(self, thread_count):
        self.thread_count = thread_count
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=thread_count)
        self.futures = []

    def submit_task(self, target):
        future = self.executor.submit(target.run)
        self.futures.append(future)

    def wait_for_completion(self):
        for future in concurrent.futures.as_completed(self.futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error in thread: {e}")

    def cleanup(self):
        self.executor.shutdown()

        
def listen_messages(self, socket,function = None):
    while True:
        try:
            data = socket.recv(1024).decode("utf-8")
            if not data:
                print("Conexão fechada pelo servidor.")
                break

        except Exception as e:
            print("Ocorreu um erro ao receber dados:", e)
            break 

class MainCode(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        
        self.target_id_enabled = False
        self.connect_enabled = False
        self.circle_color = 'gray'  # Cor inicial do círculo
        
        self.status_label = Label(text='Status:')
        self.status_image = Image(source=self.get_circle_image_path())
        
        self.connect_button = Button(text='Connect', on_press=self.on_connect)
        
        layout.add_widget(self.status_label)
        layout.add_widget(self.status_image)
        layout.add_widget(self.connect_button)
        
        # Window.size = (400, 300)
        
        return layout
    
    def get_circle_image_path(self):
        return f'circle_{self.circle_color}.png'
    
    @mainthread
    def update_ui(self,target_id_enabled:bool,connect_enabled:bool, new_circle_color:int,):
        self.target_id_enabled = target_id_enabled
        self.connect_enabled = connect_enabled
        self.status_circle_color = new_circle_color
        self.status_label.text = 'Connected support!'
        
    def on_connect(self, instance):
        match_value = instance  # Valor de correspondência (substitua pelo valor real)
        
        # Lógica de correspondência para determinar a cor do círculo
        if match_value == 1:
            new_color = 'green'  # Verde
        elif match_value == 2:
            new_color = 'yellow'  # Amarelo
        elif match_value == 3:
            new_color = 'red'  # Vermelho
        else:
            new_color = 'gray'  # Cinza
        
        self.update_ui(False,False,new_color)
        
if __name__ == "__main__":
    id_ = ''
    thread_count = 4
    manager = ThreadManager(thread_count)
    
    handlers  = [MainHandle, DesktopHandler, KeyboardHandler, FileShareHandler]
    send_types = [b'<|MAINSOCKET|>',f'<|DESKTOPSOCKET|>{id_}<|END|>'.encode("utf-8"),f'<|FILESSOCKET|>{id_}<|END|>'.encode("utf-8"),f'<|KEYBOARDSOCKET|>{id_}<|END|>'.encode("utf-8")]

    for handler, send_type in zip(handlers, send_types):
        socket_instance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            socket_instance.connect((SERVER_HOST, SERVER_PORT))
            socket_instance.send(send_type)
        except Exception as e:
            print(f"Erro ao conectar {handler.__name__}:", e)
            continue
 
        # handler_instance = handler(socket_instance)
        manager.submit_task(handler(socket_instance))


    manager.wait_for_completion()
    manager.cleanup()

    print("All processing is complete.")


    client = Client()
    client.start()
