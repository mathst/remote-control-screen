import zlib
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
# from kivy.uix.maskedinput import MaskedTextInput
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics.texture import Texture
import socket
import threading
import time
import os


class MainWindow(BoxLayout):
    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)
        self.host = '192.168.1.100'  # Insira o endereço do servidor aqui
        self.port = 3398  # Insira a porta do servidor aqui
        self.main_socket = None
        self.my_id = ''
        self.connected = False
        self.status_image = Image(source='disconnected_icon.png')
        self.status_label = Label(text='Disconnected')
        self.ids_layout = BoxLayout(orientation='horizontal')
        self.ids_layout.add_widget(Label(text='Target ID:'))
        self.ids.target_id_input = TextInput(multiline=False)
        self.ids.connect_button = Button(text='Connect', on_press=self.connect)
        self.ids_layout.add_widget(self.ids.target_id_input)
        self.ids_layout.add_widget(self.ids.connect_button)
        self.add_widget(self.ids_layout)
        self.add_widget(self.status_image)
        self.add_widget(self.status_label)

    def connect(self, *args):
        target_id = self.ids.target_id_input.text.strip()
        if target_id and target_id != '   -   -   ':
            if target_id == self.my_id:
                print("You cannot connect with yourself!")
                return
            try:
                self.main_socket = socket()
                self.main_socket.connect((self.host, self.port))
                self.connected = True
                self.main_socket.sendall(target_id.encode('utf-8'))
                self.ids.target_id_input.disabled = True
                self.ids.connect_button.disabled = True
                self.status_image.source = 'connected_icon.png'
                self.status_label.text = 'Finding the ID...'
            except Exception as e:
                print("Error connecting to the server:", e)

    def on_connected(self, *args):
        self.main_socket.sendall(self.my_id.encode('utf-8'))

    def on_disconnected(self, *args):
        self.connected = False
        self.ids.target_id_input.disabled = False
        self.ids.connect_button.disabled = False
        self.status_image.source = 'disconnected_icon.png'
        self.status_label.text = 'Disconnected from the server!'

    def on_socket_error(self, *args):
        pass

    def start_desktop_socket(self):
        self.desktop_socket = socket()
        try:
            self.desktop_socket.connect((self.host, self.port))
            self.desktop_socket.sendall(self.my_id.encode('utf-8'))
            desktop_thread = threading.Thread(target=self.desktop_socket_thread)
            desktop_thread.daemon = True
            desktop_thread.start()
        except Exception as e:
            print("Error connecting to desktop socket:", e)

    def desktop_socket_thread(self):
        while self.connected:
            try:
                data = self.desktop_socket.recv(1024)
                if not data:
                    break
                # Implementar lógica para processar os dados recebidos do socket de desktop
            except Exception as e:
                print("Error receiving data from desktop socket:", e)
                break
            
    def start_keyboard_socket(self):
        self.keyboard_socket = socket()
        try:
            self.keyboard_socket.connect((self.host, self.port))
            self.keyboard_socket.sendall(self.my_id.encode('utf-8'))
            keyboard_thread = threading.Thread(target=self.keyboard_socket_thread)
            keyboard_thread.daemon = True
            keyboard_thread.start()
        except Exception as e:
            print("Error connecting to keyboard socket:", e)

    def keyboard_socket_thread(self):
        while self.connected:
            try:
                data = self.keyboard_socket.recv(1024)
                if not data:
                    break
                # Implementar lógica para processar os dados recebidos do socket de teclado
            except Exception as e:
                print("Error receiving data from keyboard socket:", e)
                break

    def start_files_socket(self):
        self.files_socket = socket()
        try:
            self.files_socket.connect((self.host, self.port))
            self.files_socket.sendall(self.my_id.encode('utf-8'))
            files_thread = threading.Thread(target=self.files_socket_thread)
            files_thread.daemon = True
            files_thread.start()
        except Exception as e:
            print("Error connecting to files socket:", e)

    def files_socket_thread(self):
        while self.connected:
            try:
                data = self.files_socket.recv(1024)
                if not data:
                    break
                # Implementar lógica para processar os dados recebidos do socket de arquivos
            except Exception as e:
                print("Error receiving data from files socket:", e)
                break

class RemoteScreen(BoxLayout):
    def clear_connection(self):
        # Defina a lógica para limpar a conexão (frm_RemoteScreen)
        self.ids.mouse_icon_image.source = 'mouse_icon_unchecked.png'
        self.ids.keyboard_icon_image.source = 'keyboard_icon_unchecked.png'
        self.ids.resize_icon_image.source = 'resize_icon_checked.png'

        self.ids.mouse_remote_checkbox.active = False
        self.ids.keyboard_remote_checkbox.active = False
        self.ids.resize_checkbox.active = True
        # ... Outras atualizações de widgets necessárias ...

class ShareFilesScreen(BoxLayout):
    def clear_connection(self):
        # Defina a lógica para limpar a conexão (frm_ShareFiles)
        self.ids.download_bitbtn.disabled = False
        self.ids.upload_bitbtn.disabled = False
        self.ids.download_progressbar.value = 0
        self.ids.upload_progressbar.value = 0
        self.ids.size_download_label.text = 'Size: 0 B / 0 B'
        self.ids.size_upload_label.text = 'Size: 0 B / 0 B'
        # ... Outras atualizações de widgets necessárias ...

class ChatScreen(BoxLayout):
    def clear_connection(self):
        # Defina a lógica para limpar a conexão (frm_Chat)
        self.width = 230
        self.height = 340
        self.x = Window.width - self.width
        self.y = Window.height - self.height
        self.ids.chat_richedit.text = ''
        self.ids.your_text_edit.text = ''
        self.ids.chat_richedit.text += 'AllaKore Remote - Chat\n\n'
        self.ids.chat_richedit.text += 'Other initializations...'
        # ... Outras atualizações de widgets necessárias ...

class TargetIDScreen(BoxLayout):
    def connect_button_clicked(self):
        # Implemente a lógica para tratar o clique no botão "Connect"
        target_id = self.ids.target_id_maskedit.text
        # Implemente a lógica para lidar com a conexão ao ID de destino
        # ...

        # Após a conexão, atualize as outras telas usando os identificadores
        self.ids.remote_screen.clear_connection()
        self.ids.share_files_screen.clear_connection()
        self.ids.chat_screen.clear_connection()

class CustomImageButton(ButtonBehavior, Image):
    pass

class CentralConnection:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            return True
        except Exception as e:
            print("Error connecting to the server:", e)
            self.connected = False
            return False

    def receive_data(self):
        try:
            if self.connected:
                data = self.socket.recv(1024).decode('utf-8')
                if not data:
                    self.connected = False
                return data
            else:
                return None
        except Exception as e:
            print("Error receiving data:", e)
            self.connected = False
            return None

    def send_data(self, data):
        try:
            if self.connected:
                self.socket.sendall(data.encode('utf-8'))
            else:
                print("Not connected to the server.")
        except Exception as e:
            print("Error sending data:", e)
            self.connected = False

    def execute(self):
        while self.connected:
            time.sleep(0.05)  # Avoid using 100% CPU
            data = self.receive_data()
            if data:
                # Process the received data and take actions accordingly
                self.process_data(data)

class Tfrm_Main(BoxLayout):
    def __init__(self, **kwargs):
        super(Tfrm_Main, self).__init__(**kwargs)

        # ... Rest of the UI setup ...

        # Create the CentralConnection instance
        self.central_connection = CentralConnection('api.sdremoto.com.br', 6651)
        self.central_connection.connect()

    def on_keyboard_down(self, keycode, scancode, text, modifiers):
        # Handle keyboard down event
        # Convert the input data to bytes and send it via CentralConnection
        data = f'<|KEYBOARD_DOWN|>{keycode[0]}<|>{scancode}<|>{text}<|>{modifiers}<|>'
        self.central_connection.send_data(data)

    def on_keyboard_up(self, keycode):
        # Handle keyboard up event
        # Convert the input data to bytes and send it via CentralConnection
        data = f'<|KEYBOARD_UP|>{keycode[0]}<|>'
        self.central_connection.send_data(data)

    def on_touch_down(self, touch):
        # Handle mouse click event
        # Convert the input data to bytes and send it via CentralConnection
        data = f'<|MOUSE_CLICK|>{touch.x}<|>{touch.y}<|>'
        self.central_connection.send_data(data)

    def on_touch_up(self, touch):
        # Handle mouse release event
        # Convert the input data to bytes and send it via CentralConnection
        data = f'<|MOUSE_RELEASE|>{touch.x}<|>{touch.y}<|>'
        self.central_connection.send_data(data)

    # Add other methods to handle mouse move, file transfer, clipboard, etc.

    def update(self, dt):
        # Periodically check for received data from the server
        data = self.central_connection.receive_data()
        if data:
            self.central_connection.process_data(data)

    def on_close(self):
        # Close the central connection when the app is closed
        pass

class App(App):
    def build(self):
        frm_main = Tfrm_Main()
        # Bind keyboard and mouse events to the Tfrm_Main instance
        Window.bind(on_keyboard=frm_main.on_keyboard_down, on_keyboard_up=frm_main.on_keyboard_up,
                    on_touch_down=frm_main.on_touch_down, on_touch_up=frm_main.on_touch_up)
        # Schedule the update method to run periodically
        Clock.schedule_interval(frm_main.update, 0.1)
        return frm_main

    def compress_stream_with_zlib(src_stream):
        try:
            in_data = src_stream.getvalue()
            compressed_data = zlib.compress(in_data, level=zlib.Z_DEFAULT_COMPRESSION)
            src_stream.seek(0)
            src_stream.truncate(0)
            src_stream.write(compressed_data)
            return True
        except Exception as e:
            print("Error compressing stream:", e)
            return False

    def decompress_stream_with_zlib(src_stream):
        try:
            in_data = src_stream.getvalue()
            decompressed_data = zlib.decompress(in_data)
            src_stream.seek(0)
            src_stream.truncate(0)
            src_stream.write(decompressed_data)
            return True
        except Exception as e:
            print("Error decompressing stream:", e)
            return False

    def memory_stream_to_string(memory_stream):
        return memory_stream.getvalue().decode('utf-8')
    
if __name__ == '__main__':
    App().run()
