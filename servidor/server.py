import json
import socket
import threading
import time
import numpy as np
import pyautogui
from mss import mss
import cv2
import concurrent.futures
import lz4.frame

from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController

SERVER_HOST = '10.200.0.17'
COMMAND_PORT = 3081
SCREEN_PORT = 3080
screen_width, screen_height = pyautogui.size()


class ComandsEventHandling:#ETIQUETA DE ALGO QUE VIA SER USADO=
    def __init__(self):
        self.mouse_c = MouseController()
        self.keyboard_c = KeyboardController()

        
    def on_move(self,x,y):
        self.mouse_c.move(x, y)
        print("o mouse foi para: ",x,';',y)
        self.mouse_position=x,y
        
    def on_click(self,button):
        if button == 'Button.left':
            self.mouse_c.click(Button(1))
            print("click botão 1")
        elif button == 'Button.middle':
            self.mouse_c.click(Button(2))
            print("click botão 2")
        elif button == 'Button.right':
            self.mouse_c.click(Button(3))
            print("click botão 3")

    def on_scroll(self,dx,dy):
        self.mouse_c.scroll(dx,dy)
        print("scroll")
  
    def on_press(self, command):
        if command.startswith("Key."):
            key_name = command.split(".")[1]  # Extrai o nome da tecla
            key = self.get_key(key_name)
            self.keyboard_c.press(key)  # Pressiona a tecla
        else:   
            self.keyboard_c.press(command)  # Pressiona a tecla

    def on_release(self, command):
        if command.startswith("Key."):
            key_name = command.split(".")[1]  # Extrai o nome da tecla
            key = self.get_key(key_name)
            self.keyboard_c.release(key)  # Libera a tecla
        else:
            self.keyboard_c.release(command)  # Libera a tecla

    def get_key(self, key_name):
        try:
            # Tentar pegar a tecla pelo atributo
            return getattr(Key, key_name)
        except AttributeError:
            # A tecla não existe em `Key`, retornar `None`
            return None

class Server:
    def __init__(self):
        self.command_socket = None
        self.screen_socket = None
        self.running = True
        self.last_screen = None
        self.frame_rate = 30  # Limita a taxa de quadros para 30 FPS

        self.comands_event_handling = ComandsEventHandling()
        self.reference_frame = None
        self.frame_counter = 0
        self.N = 10

    @property
    def mouse_position(self):
        # Retorna a posição atual do mouse como uma tupla
        return MouseController.position

    def start(self):
        self.command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.command_socket.bind((SERVER_HOST, COMMAND_PORT))
        self.command_socket.listen(1)
        print(f"Servidor iniciado. Aguardando conexões em {SERVER_HOST}:{COMMAND_PORT}")

        self.screen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.screen_socket.bind((SERVER_HOST, SCREEN_PORT))
        self.screen_socket.listen(1)
        print(f"Servidor de compartilhamento de tela iniciado. Aguardando conexões em {SERVER_HOST}:{SCREEN_PORT}")

        try:
            while self.running:
                try:
                    command_conn, addr = self.command_socket.accept()
                    print(f"Cliente de comandos conectado: {addr}")
                    
                    self.send_screen_dimensions(screen_width, screen_height, command_conn)

                    screen_conn, addr = self.screen_socket.accept()
                    print(f"Cliente de compartilhamento de tela conectado: {addr}")
                    
                    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                        executor.submit(self.send_screen, screen_conn)
                        print("Threads tela.")
                        executor.submit(self.receive_commands, command_conn)         
                        print("Threads comand.")
   
                except KeyboardInterrupt:
                    print("Servidor encerrado.")
                    self.command_socket.close()
                    self.screen_socket.close()
                    self.running = False
                    break
                 
        except Exception as e:
            print(f"Erro: {e}")
            self.command_socket.close()
            self.screen_socket.close()
            self.running = False
            
        except KeyboardInterrupt:
            print("Servidor encerrado.")
            self.command_socket.close()
            self.screen_socket.close()
            self.running = False

                      

    def excutc_command(self, command):
        commandT = command['type']
        
        if commandT == 'press':
            commandK = command['key']
            self.comands_event_handling.on_press(commandK)     
                   
        elif commandT == 'release':
            commandK = command['key']
            self.comands_event_handling.on_release(commandK)
            
        elif commandT == 'move':
            dx=command['x']
            dy=command['y']
            self.comands_event_handling.on_move(dx,dy)
            
        elif commandT == 'click':
            det=command['details']
            button=det['button']
            self.comands_event_handling.on_click(button)
            
        elif commandT == 'scroll':
            det=command['details']
            dx=det['x']
            dy=det['y']
            self.comands_event_handling.on_scroll(dx,dy)
            
        else:
            print(f"Comando inválido mouse: {command}")
            
    def receive_commands(self, conn):
        while self.running:
            try:
                data = ''
                conn.settimeout(10.0)
                while self.running:
                    part = conn.recv(1024).decode()
                    data += part

                    # Verifica se a parte recebida contém o terminador
                    if '}\n' in part:
                        break

                commands = self.split_data_into_commands(data)
                for command in commands:
                    # sai da lista
                    try:
                        command = json.loads(command)
                        self.excutc_command(command) 
 
                    except (Exception,KeyError, json.JSONDecodeError) as e:
                        print(f"Comando inválido geral: {command}. Erro: {str(e)}")

            except Exception as e:
                print(f"Erro ao receber comandos: {str(e)}")
            
            except KeyboardInterrupt:
                print("Servidor de comando encerrado.")
                conn.close()
                self.running = False

    def split_data_into_commands(self, data):
        """Divide os dados em comandos individuais."""
        commands = []
        while data:
            try:
                command, data = data.split('\n', 1)
                commands.append(command)
            except ValueError:  # Não há mais caracteres de nova linha
                break
        return commands
    
    def send_screen_dimensions(self, width, height, connection):
        # Prepare os dados
        data = {"width": width, "height": height}
        json_data = json.dumps(data)
        print("enviou dimensoes")
        # Envie os dados
        connection.sendall(json_data.encode('utf-8'))


    def overlay_cursor_on_screen(self, screen, position):
        x, y = position
        radius = 5  # você pode ajustar o tamanho do círculo aqui
        color = (255, 255, 255)  # cor branca
        thickness = -1  # preenche o círculo
        # Converte o objeto de tela em uma matriz NumPy
        screen_np = np.array(screen)
        # Desenha o círculo na imagem da tela na posição do cursor
        cv2.circle(screen_np, (x, y), radius, color, thickness)
        return screen_np  # Retorna a matriz NumPy com o cursor desenhado


    def serialize_screen(self, screen_np):
        screenA = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
        _, encoded_screen = cv2.imencode('.jpg', screenA, [int(cv2.IMWRITE_JPEG_QUALITY), 70])  # Reduz a qualidade do JPEG para economizar memória
        compressed_screen = lz4.frame.compress(encoded_screen)  # Comprimindo o frame
        return compressed_screen
    
    def capture_screen(self):
            with mss() as sct:
                # Quadro de referência
                if self.reference_frame is None:
                    self.reference_frame = np.array(sct.grab(sct.monitors[0]))

                # Capture o quadro atual
                screen = sct.grab(sct.monitors[0])
                
                # Agora o método retorna uma matriz NumPy
                screen_np = self.overlay_cursor_on_screen(screen, self.mouse_position)
        
                # Aplicamos um filtro de suavização
                screen_np = cv2.GaussianBlur(screen_np, (5, 5), 0)
        
                # Calculamos a diferença entre o quadro atual e o quadro de referência
                frame_diff = cv2.absdiff(self.reference_frame, screen_np)
        
                # Aplicamos um limiar para binarizar a imagem de diferença
                _, threshold_diff = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)
        
                # Incrementamos o contador de quadros
                self.frame_counter += 1
        
                # A cada N quadros, enviamos o quadro completo. Nos outros quadros, enviamos a diferença
                if self.frame_counter % self.N == 0:
                    frame_data = self.serialize_screen(screen_np)
                else:
                    frame_data = self.serialize_screen(threshold_diff)
        
                # Atualizamos o quadro de referência
                self.reference_frame = screen_np

                return frame_data

    def send_screen(self, conn):
        while self.running:
            print ("enviando tela")
            screen_data = self.capture_screen()
            if screen_data is not None:
                print("enviou tela",len(screen_data))
                conn.sendall(screen_data)
            else:
                time.sleep(0.005)# evita que o loop consuma todos os recursos do CPU
                
        conn.close()


if __name__ == "__main__":  
    server = Server()
    server.start()