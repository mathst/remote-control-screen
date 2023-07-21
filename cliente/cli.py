import os
import socket
import concurrent.futures
import asyncio
import threading
import time
import zlib
import pyperclip
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.core.window import Window

# Importe todas as telas aqui
from screens.login import LoginScreen
from screens.share_screen import ShareScreen
from screens.file_share import FileShareScreen
from screens.chat import ChatScreen

MyID = "YourID"  # mais para frente ele vai ser gerado junto com o password
server_ip = "127.0.0.1"  # IP do servidor
server_port = 12345  # Porta do servidor

    
class SocketCreator:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None

    def create(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind((self.host, self.port))
            print(f"Socket created on {self.host}:{self.port}")
        except Exception as e:
            print("Error creating socket:", e)

    def start_listening(self):
        if not self.socket:
            print("Socket not created. Call create() method first.")
            return
        
        self.socket.listen()
        print("Socket is listening...")

        while True:
            try:
                conn, addr = self.socket.accept()
                # Aqui, você pode enviar a conexão (conn) e o endereço (addr) para outra classe ou função
                # para processar o cliente conectado. Por exemplo, em asyncio, você pode usar coroutines.
            except Exception as e:
                print("Error accepting connection:", e)

    def stop(self):
        if self.socket:
            self.socket.close()
            
class ParallelExecutor:
    def __init__(self, func):
        self.func = func

    def run_threads(self, args_list):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.func, *args) for args in args_list]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        return results

    async def run_asyncio(self, args_list):
        tasks = [self.func(*args) for args in args_list]
        results = await asyncio.gather(*tasks)
        return results
# executor = ParallelExecutor(minha_func)

# # Executar usando threading
# args_list = [1, 2, 3, 4, 5]
# results_with_threads = executor.run_threads(args_list)
# print(results_with_threads)  # Resultado: [2, 4, 6, 8, 10]

# # Executar usando asyncio
# args_list = [1, 2, 3, 4, 5]
# loop = asyncio.get_event_loop()
# results_with_asyncio = loop.run_until_complete(executor.run_asyncio(args_list))
# print(results_with_asyncio)  # Resultado: [2, 4, 6, 8, 10]

class ConnectionManager:
    def __init__(self):
        self.screen_manager = ScreenManager()
        self.viewer = False
        self.main_socket = None
        self.desktop_socket = None
        self.keyboard_socket = None
        self.files_socket = None

    def create_and_start_sockets(self):
        socket_creator = SocketCreator(server_ip, server_port)

        # Main Socket
        self.main_socket = socket_creator.create_and_start_listening()
        if not self.main_socket:
            return False

        # Desktop Socket
        self.desktop_socket = socket_creator.create_and_start_listening()
        if not self.desktop_socket:
            return False

        # Keyboard Socket
        self.keyboard_socket = socket_creator.create_and_start_listening()
        if not self.keyboard_socket:
            return False

        # Files Socket
        self.files_socket = socket_creator.create_and_start_listening()
        if not self.files_socket:
            return False

        return True

    def close_sockets(self):
        for sock in [self.main_socket, self.desktop_socket, self.keyboard_socket, self.files_socket]:
            if sock:
                sock.close()

        self.viewer = False
        self.clear_connections

class decodificador:
    def __init__(self, src_stream):
        self.src_stream = src_stream

    def compress_stream(self):
        try:
            input_data = self.src_stream.getvalue()
            compressed_data = zlib.compress(input_data, level=zlib.Z_DEFAULT_COMPRESSION)
            self.src_stream.seek(0)
            self.src_stream.truncate(0)
            self.src_stream.write(compressed_data)
            return True
        except Exception as e:
            print("Error compressing stream:", e)
            return False

    def decompress_stream(self):
        try:
            input_data = self.src_stream.getvalue()
            decompressed_data = zlib.decompress(input_data)
            self.src_stream.seek(0)
            self.src_stream.truncate(0)
            self.src_stream.write(decompressed_data)
            return True
        except Exception as e:
            print("Error decompressing stream:", e)
            return False


class MessageReceiver(threading.Thread):
    def __init__(self, socket):
        super().__init__()
        self.socket = socket
        self.is_active = True

    def run(self):
        while self.is_active:
            try:
                data = self.socket.recv(1024).decode()  # Receive data from the server
                # Process the received data here
                print("Received data:", data)
            except Exception as e:
                print("Error receiving data:", e)
                break



def get_size(bytes):
    bytes = int(bytes)
    if bytes < 1024:
        return f"{bytes} B"
    elif bytes < 1048576:  # 1024 * 1024
        return f"{bytes / 1024:.1f} KB"
    elif bytes < 1073741824:  # 1024 * 1024 * 1024
        return f"{bytes / 1048576:.1f} MB"
    else:
        return f"{bytes / 1073741824:.1f} GB"

def list_folders(directory):
    dir_list = []
    for entry in os.scandir(directory):
        if entry.is_dir():
            dir_list.append(entry.name)
    return '\n'.join(dir_list)

def list_files(directory, ext):
    file_list = []
    for entry in os.scandir(directory):
        if entry.is_file() and entry.name.endswith(ext):
            file_list.append(entry.name)
    return '\n'.join(file_list)

def reconnect(socket):
    if not socket.is_active():
        socket.is_active = True
        
def reconnect_secundary_sockets(desktop_socket, keyboard_socket, files_socket):
    viewer = False

    desktop_socket.close()
    keyboard_socket.close()
    files_socket.close()

    # Aguardar a desconexão (Workaround)
    time.sleep(1)

    desktop_socket.is_active = True
    keyboard_socket.is_active = True
    files_socket.is_active = True

class MainWindow(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.old_clipboard_text = ""
        self.main_socket = socket

    def clear_connection(self):
        self.width = 600
        self.height = 986

    def clipboard_timer(self, dt):
        try:
            clipboard_text = pyperclip.paste()
            if clipboard_text and clipboard_text != self.old_clipboard_text:
                self.old_clipboard_text = clipboard_text
                try:
                    # Envie os dados para o servidor usando o método apropriado, como no exemplo abaixo:
                    self.main_socket.sendall(bytes(f'[CLIPBOARD]{clipboard_text}[/CLIPBOARD]', 'utf-8'))
                except Exception as e:
                    print(f"Error sending clipboard data: {e}")
        except Exception as e:
            print(f"Error accessing clipboard: {e}")

    def set_connected(self):
        self.ids.your_id_edit.text = 'Receiving...'
        self.ids.your_id_edit.disabled = True

        self.ids.your_password_edit.text = 'Receiving...'
        self.ids.your_password_edit.disabled = True

        self.ids.target_id_edit.text = ''
        self.ids.target_id_edit.disabled = True

        self.ids.connect_button.disabled = True

    def set_online(self):
        self.ids.your_id_edit.text = MyID
        self.ids.your_id_edit.disabled = False

        self.ids.your_password_edit.text = MyPassword
        self.ids.your_password_edit.disabled = False

        self.ids.target_id_edit.text = ''
        self.ids.target_id_edit.disabled = False

        self.ids.connect_button.disabled = False

    def connect_button_click(self):
        target_id = self.ids.target_id_edit.text.strip().replace('-', '')

        if not target_id:
            return

        if target_id == MyID:
            self.show_popup('You can not connect with yourself!')
        else:
            # Enviar a ID para o socket ou fazer outras operações aqui
            # ('' + TargetID_MaskEdit.Text + '')
            self.ids.target_id_edit.disabled = True
            self.ids.connect_button.disabled = True
            self.update_status('Finding the ID...')

    def show_popup(self, message):
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text=message))
        close_button = Button(text='Close')
        popup = Popup(title='', content=content, size_hint=(None, None), size=(400, 200))

        def close_popup(instance):
            popup.dismiss()

        close_button.bind(on_release=close_popup)
        content.add_widget(close_button)
        popup.open()

    def update_status(self, message):
        self.ids.status_label.text = message
        self.ids.status_image.source = 'path_to_your_image.png'  # Substitua pelo caminho correto para a imagem


class MApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connection_manager = ConnectionManager()

    def build(self):
        # Defina o tamanho da janela principal
        Window.size = (800, 600)

        # Carrega os arquivos KV
        Builder.load_file('ui/login.kv')
        Builder.load_file('ui/share_screen.kv')
        Builder.load_file('ui/file_share_screen.kv')
        Builder.load_file('ui/chat_screen.kv')

        # Cria o gerenciador de telas (ScreenManager)
        sm = ScreenManager()

        # Adiciona as telas ao gerenciador de telas
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(ShareScreen(name='share'))
        sm.add_widget(FileShareScreen(name='file_share'))
        sm.add_widget(ChatScreen(name='chat'))

        # Salva a referência do ScreenManager para que outros métodos possam acessá-lo
        self.screen_manager = sm
        return sm

    def on_start(self):
        # Crie e inicie os sockets
        if not self.connection_manager.create_and_start_sockets():
            # Trate o caso em que a criação dos sockets falha
            print("Failed to create and start sockets.")

        # Inicie a thread para receber mensagens do servidor
        message_receiver = MessageReceiver(self.connection_manager.main_socket)
        message_receiver.start()

    def on_stop(self):
        # Ao sair do aplicativo, feche as conexões
        self.connection_manager.close_sockets()