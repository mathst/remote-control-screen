# dict <--->json

# Para transformar um JSON para um dicionário 
# # uma string JSON
json_string = '{"nome":"João", "idade": 30}'

# # convertendo a string JSON para um dicionário
dict_obj = json.loads(json_string)

print(dict_obj)  # Saída: {'nome': 'João', 'idade': 30}






# Para transformar um dicionário para um JSON

# # um dicionário
dict_obj = {'nome': 'João', 'idade': 30}

# # convertendo o dicionário para uma string JSON
json_string = json.dumps(dict_obj)

print(json_string)  # Saída: '{"nome": "João", "idade": 30}'

data = {"x": 10, "y": 20, "name": "example"}

import json

with open('data.json', 'w') as f:
    json.dump(data, f)




string_data = "Hello, world!"
byte_data = string_data.encode('utf-8')  # converte a string para bytes usando a codificação UTF-8


byte_data = socket.recv(1024)  # recebe até 1024 bytes do socket
string_data = byte_data.decode('utf-8')  # converte os bytes para uma string usando a codificação UTF-8




import json

# Dicionário original
original_dict = {"chave": "valor", "número": 123}

# Converte o dicionário em uma string JSON
json_string = json.dumps(original_dict)

# Converte a string JSON em bytes
byte_data = json_string.encode('utf-8')

# Agora você tem seus dados como bytes e pode enviá-los pela rede
# ...

# Para converter de volta em um dicionário:
# Primeiro decodifica os bytes para uma string
received_string = byte_data.decode('utf-8')

# Então converte a string JSON de volta em um dicionário
received_dict = json.loads(received_string)

assert original_dict == received_dict  # Deve ser True


Ao usar o método `str.encode()`, o padrão é codificar a string como UTF-8. O UTF-8 é um formato de codificação de caracteres que pode representar qualquer caractere no conjunto de caracteres Unicode. Ele é comumente usado na web e em outros lugares devido à sua capacidade de representar uma ampla variedade de caracteres de diferentes scripts e idiomas.

Se você quiser explicitamente definir a codificação como UTF-8, você pode fazer isso da seguinte maneira: 

```python
conn.sendall((json_data + '\n').encode('utf-8'))
```

No entanto, na prática, muitas vezes é suficiente simplesmente usar o método `str.encode()` sem especificar uma codificação, pois o UTF-8 é o padrão.

Também é importante lembrar que a decodificação (o processo de transformar bytes de volta em uma string) também deve usar a mesma codificação. Se você codificar uma string como UTF-8, também deve decodificá-la como UTF-8. Caso contrário, você pode acabar com caracteres incorretos ou erros.


Entendo que o código que você descreveu parece estar aninhado demais e pode ser difícil de entender e gerenciar. Aqui estão algumas sugestões para melhorar a estrutura do seu código:

1. **Evite muitos níveis de aninhamento**: Muitos níveis de aninhamento podem tornar o código difícil de ler e de manter. Pode ser útil dividir o código em funções menores que têm responsabilidades claramente definidas.

2. **Tratamento de erros**: A cláusula try/except é útil para o tratamento de erros, mas pode ser abusada. Idealmente, você deve tentar evitar erros, em vez de simplesmente tratá-los após o fato. Além disso, é melhor ter cláusulas try/except mais específicas que capturam e lidam apenas com tipos de erros conhecidos e esperados, em vez de usar uma cláusula genérica que pode mascarar erros inesperados.

3. **Use declarações if/elif/else de maneira eficiente**: Muitas vezes, você pode reestruturar suas condições para torná-las mais eficientes. Por exemplo, se você tem várias condições que são mutuamente exclusivas, você pode usar a declaração elif para garantir que apenas a condição correta seja verificada. Além disso, se uma condição é muito mais provável de ser verdadeira do que as outras, você pode verificar essa condição primeiro para economizar algum tempo de processamento.

4. **Evite loops desnecessários**: Se você tem loops dentro de loops (como um loop for dentro de um loop while), o tempo de processamento pode aumentar rapidamente, especialmente para grandes conjuntos de dados. Se possível, tente reestruturar o código para evitar esses loops aninhados.

Aqui está um exemplo de como você poderia reestruturar um código similar ao que você descreveu:

```python
def process_data(data):
    for item in data:
        try:
            if condition1(item):
                handle_condition1(item)
            elif condition2(item):
                handle_condition2(item)
            else:
                handle_default_condition(item)
        except KnownError:
            handle_known_error(item)
        except Exception as e:
            handle_unknown_error(e)

def condition1(item):
    return item == "condition1"

def condition2(item):
    return item == "condition2"

def handle_condition1(item):
    print(f"Handled condition1 for item {item}")

def handle_condition2(item):
    print(f"Handled condition2 for item {item}")

def handle_default_condition(item):
    print(f"Handled default condition for item {item}")

def handle_known_error(item):
    print(f"Handled known error for item {item}")

def handle_unknown_error(e):
    print(f"Unhandled exception: {e}")

while True:
    try:
        data = fetch_data()
        process_data(data)
    except FetchDataError:
        handle_fetch_data_error()
```

Note que esse é um exemplo muito geral. Dependendo do seu caso específico, outras estratégias de refatoração podem ser mais apropriadas.


def deserialize_screen(self, serialized_screen):
        compressed_screen = np.frombuffer(serialized_screen, dtype=np.uint8)
        encoded_screen = lz4.frame.decompress(compressed_screen)
        screen = cv2.imdecode(encoded_screen, cv2.IMREAD_COLOR)
        return screen

Aqui está um exemplo de como você pode usar a biblioteca `pynput` para detectar pressionamentos de teclas e a biblioteca `subprocess` para executar comandos de shell com base nesses pressionamentos de teclas.

Este é um exemplo simplista e você deve modificar o comando e a combinação de teclas para se adequar às suas necessidades. Além disso, esteja ciente dos perigos potenciais de executar comandos de shell desta maneira.

```python
from pynput import keyboard
import subprocess

# Definindo a ação para a combinação de teclas
def on_activate():
    print('Atalho pressionado')
    # Executando um comando de shell
    subprocess.run(["ls", "-l"])

# Definindo a combinação de teclas
hotkey = '<ctrl>+<alt>+h'

# Criando um mapeamento entre a combinação de teclas e a ação
key_map = {hotkey: on_activate}

# Iniciando o listener de teclas
with keyboard.GlobalHotKeys(key_map) as h:
    h.join()
```

No exemplo acima, quando você pressionar `<ctrl>+<alt>+h`, o script imprimirá "Atalho pressionado" e executará o comando `ls -l`.

Lembre-se, o `ls -l` é um comando do Linux que lista os arquivos em um diretório. Se você estiver no Windows, precisará usar um comando compatível com o Windows. Além disso, este comando será executado no diretório atual do script, então você pode querer especificar um caminho de diretório se precisar que ele seja executado em um local específico.



Windowns
from pynput import keyboard

# Funções de atalho
def on_activate_ctrl_c():
    print('<ctrl>+c pressed')

def on_activate_ctrl_v():
    print('<ctrl>+v pressed')

def on_activate_ctrl_x():
    print('<ctrl>+x pressed')

def on_activate_ctrl_z():
    print('<ctrl>+z pressed')

def on_activate_ctrl_y():
    print('<ctrl>+y pressed')

def on_activate_ctrl_a():
    print('<ctrl>+a pressed')

def on_activate_ctrl_s():
    print('<ctrl>+s pressed')

def on_activate_ctrl_o():
    print('<ctrl>+o pressed')

def on_activate_alt_tab():
    print('<alt>+<tab> pressed')

def on_activate_alt_f4():
    print('<alt>+f4 pressed')

def on_activate_ctrl_shift_esc():
    print('<ctrl>+<shift>+<esc> pressed')

def on_activate_win_l():
    print('<win>+l pressed')

def on_activate_win_d():
    print('<win>+d pressed')

# Registrando as funções de atalho
with keyboard.GlobalHotKeys({
        '<ctrl>+c': on_activate_ctrl_c,
        '<ctrl>+v': on_activate_ctrl_v,
        '<ctrl>+x': on_activate_ctrl_x,
        '<ctrl>+z': on_activate_ctrl_z,
        '<ctrl>+y': on_activate_ctrl_y,
        '<ctrl>+a': on_activate_ctrl_a,
        '<ctrl>+s': on_activate_ctrl_s,
        '<ctrl>+o': on_activate_ctrl_o,
        '<alt>+<tab>': on_activate_alt_tab,
        '<alt>+f4': on_activate_alt_f4,
        '<ctrl>+<shift>+<esc>': on_activate_ctrl_shift_esc,
        '<win>+l': on_activate_win_l,
        '<win>+d': on_activate_win_d
        }) as h:
    h.join()

Linux

Aqui está um exemplo de como você poderia configurar as funções para os atalhos mais comuns no Linux usando a biblioteca `pynput`. Por favor, note que nem todos os atalhos podem ser facilmente manipulados usando esta biblioteca, devido às limitações do sistema operacional.

```python
from pynput import keyboard

# Funções de atalho
def on_activate_ctrl_c():
    print('<ctrl>+c pressed')

def on_activate_ctrl_v():
    print('<ctrl>+v pressed')

def on_activate_ctrl_x():
    print('<ctrl>+x pressed')

def on_activate_ctrl_z():
    print('<ctrl>+z pressed')

def on_activate_ctrl_a():
    print('<ctrl>+a pressed')

def on_activate_ctrl_s():
    print('<ctrl>+s pressed')

def on_activate_ctrl_o():
    print('<ctrl>+o pressed')

def on_activate_ctrl_q():
    print('<ctrl>+q pressed')

def on_activate_alt_f4():
    print('<alt>+f4 pressed')

def on_activate_alt_tab():
    print('<alt>+<tab> pressed')

def on_activate_ctrl_alt_t():
    print('<ctrl>+<alt>+t pressed')

def on_activate_ctrl_alt_l():
    print('<ctrl>+<alt>+l pressed')

def on_activate_ctrl_alt_del():
    print('<ctrl>+<alt>+del pressed')

# Registrando as funções de atalho
with keyboard.GlobalHotKeys({
        '<ctrl>+c': on_activate_ctrl_c,
        '<ctrl>+v': on_activate_ctrl_v,
        '<ctrl>+x': on_activate_ctrl_x,
        '<ctrl>+z': on_activate_ctrl_z,
        '<ctrl>+a': on_activate_ctrl_a,
        '<ctrl>+s': on_activate_ctrl_s,
        '<ctrl>+o': on_activate_ctrl_o,
        '<ctrl>+q': on_activate_ctrl_q,
        '<alt>+f4': on_activate_alt_f4,
        '<alt>+<tab>': on_activate_alt_tab,
        '<ctrl>+<alt>+t': on_activate_ctrl_alt_t,
        '<ctrl>+<alt>+l': on_activate_ctrl_alt_l,
        '<ctrl>+<alt>+del': on_activate_ctrl_alt_del,
        }) as h:
    h.join()
```
Essa solução vai apenas imprimir qual atalho foi pressionado, não vai executar as ações correspondentes ao atalho. Além disso, esse código pode não funcionar para todas as teclas de atalho, dependendo das limitações de permissões do sistema operacional e do ambiente de trabalho.

As teclas 'ctrl', 'alt', 'shift', 'esc', 'tab', etc., são todas strings usadas para representar as teclas de controle, alt, shift, escape e tab, respectivamente. Se você quiser adicionar mais atalhos, pode fazê-lo adicionando mais entradas no dicionário dentro do construtor `GlobalHotKeys`.

No código acima, nós substituímos as listas frame_buffer e command_buffer por instâncias de queue.Queue. Em seguida, substituímos as chamadas a list.append() e list.pop(0) por queue.Queue.put() e queue.Queue.get(), respectivamente. Finalmente, para recuperar todos os itens da fila, nós continuamos chamando queue.Queue.get() até a fila estar vazia.

# Criando uma instância da classe Buffering
buffering = Buffering()

# Adicionando um frame à fila frame_buffer
frame = "meu frame"
buffering.add_to_frame_buffer(frame)

# Adicionando um comando à fila command_buffer
command = "meu comando"
buffering.add_to_command_buffer(command)


class Buffering:
    def __init__(self):
        self.buffer_size_limit = 30
        self.frame_buffer = queue.Queue(maxsize=self.buffer_size_limit)
        self.command_buffer = queue.Queue(maxsize=self.buffer_size_limit)

    def add_to_frame_buffer(self, frame):
        if self.frame_buffer.full():
            self.frame_buffer.get()
        self.frame_buffer.put(frame)

    def add_to_command_buffer(self, command):
        if self.command_buffer.full():
            self.command_buffer.get()
        self.command_buffer.put(command)

    def get_frames(self):
        frames = []
        while not self.frame_buffer.empty():
            frames.append(self.frame_buffer.get())
        return frames

    def get_commands(self):
        commands = []
        while not self.command_buffer.empty():
            commands.append(self.command_buffer.get())
        return commands


        Aqui está como você poderia adaptar o código que você forneceu para separar as filas de comando para o mouse e o teclado:

```python
from queue import Queue

queue_envia_mouse = Queue()
queue_recebe_mouse = Queue()
queue_envia_teclado = Queue()
queue_recebe_teclado = Queue()

def captura_acoes_mouse(queue_envia_mouse):
    # Captura ações do mouse e coloca na fila de envio

def captura_acoes_teclado(queue_envia_teclado):
    # Captura ações do teclado e coloca na fila de envio

def empacota_e_envia(queue_envia_mouse, queue_envia_teclado):
    # Pega ações das filas de envio, empacota e envia

def recebe_e_desempacota(queue_recebe_mouse, queue_recebe_teclado):
    # Recebe ações, desempacota e coloca nas filas de recebimento

def executa_acoes(queue_recebe_mouse, queue_recebe_teclado):
    # Pega ações das filas de recebimento e executa

threading.Thread(target=captura_acoes_mouse, args=(queue_envia_mouse,)).start()
threading.Thread(target=captura_acoes_teclado, args=(queue_envia_teclado,)).start()
threading.Thread(target=empacota_e_envia, args=(queue_envia_mouse, queue_envia_teclado)).start()
threading.Thread(target=recebe_e_desempacota, args=(queue_recebe_mouse, queue_recebe_teclado)).start()
threading.Thread(target=executa_acoes, args=(queue_recebe_mouse, queue_recebe_teclado)).start()
```

Isso assume que a função `empacota_e_envia` é capaz de empacotar e enviar comandos tanto do mouse quanto do teclado e que a função `recebe_e_desempacota` é capaz de receber e desempacotar esses comandos. A função `executa_acoes` também teria que ser capaz de executar ações de ambos os tipos.

Este é apenas um exemplo de como você poderia organizar o seu código. A estrutura exata e as implementações das funções dependem das necessidades específicas do seu aplicativo. Por exemplo, você pode achar mais eficiente ter threads separadas para empacotar/enviar e receber/desempacotar comandos do mouse e do teclado, dependendo de quão pesadas são essas operações e de como elas estão distribuídas entre o mouse e o teclado.

import json
import socket
import threading
import time
import numpy as np
import pyautogui
from mss import mss
import cv2
import lz4.frame

from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController

mouse_c = MouseController()
keyboard_c = KeyboardController()

SERVER_HOST = '10.200.0.17'
PORTA_COMANDO = 3081
PORTA_TELA = 3080
largura_tela, altura_tela = pyautogui.size()

class TratamentoEventoMouse:
    def __init__(self, comando):
        self.comando = comando
        self.posicao_mouse = (0, 0)
        self.botao = comando['button']
        
    def on_move(self):
        x = self.comando['x']
        y = self.comando['y']
        self.posicao_mouse = MouseController.position
        mouse_c.move(x, y)

    def on_click(self):
        x = self.comando['x']
        y = self.comando['y']
        botao = self.comando['button']
        pressionado = self.comando['pressed']

        if botao == 'Button.left':
            self.pressed(1)
        elif botao == 'Button.right':
            self.pressed(3)
        elif botao == 'Button.middle':
            self.pressed(2)    
                
    def on_scroll(self):
        dx = self.comando['dx']
        dy = self.comando['dy']
        mouse_c.scroll(dx, dy)
        
    def pressed(self, button):
        botao_enum = Button[botao]
        if pressionado:
            mouse_c.press(botao_enum)
        else:
            mouse_c.release(botao_enum)

class TratamentoEventoTeclado:
    def __init__(self, comando):
        self.detalhes = comando['detalhes']
        self.tecla = self.detalhes['tecla']
        
    def on_press(self):
        tecla = self.tecla
        if self.tecla.startswith("Key."):
            tecla = self.tecla.split(".")[1]
            tecla = getattr(Key, tecla)    
        keyboard_c.press(tecla)

    def on_release(self):
        tecla = self.tecla
        if self.tecla.startswith("Key."):
            tecla = self.tecla.split(".")[1]
            tecla = getattr(Key, tecla)
        keyboard_c.release(tecla)

        import concurrent.futures

# No método start
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    executor.submit(self.receive_screen, self.screen_socket)
    executor.submit(self.captura_keyborad_e_mouse)
print("Threads iniciadas.")


def show_screen(self,screen):
    self.screen=screen
    def update_label():
        if self.running:
            screen = self.screen
            image = Image.fromarray(cv2.cvtColor(screen, cv2.COLOR_BGR2RGB))
            try:
                self.label.image.paste(image)
            except AttributeError:
                self.label.image = ImageTk.PhotoImage(image)
                self.label.configure(image=self.label.image)
        else:
            self.root.after(10, update_label)
        # Forçar a coleta de lixo após atualizar a imagem
        gc.collect()

    update_label()
    self.root.mainloop()


    import gc

    # Chamar o garbage collector
    gc.collect()


        def start(self):
            self.root.title(WINDOW_TITLE)
            # Receba as dimensões da tela do servidor
            self.receive_screen_dimensions(self.command_socket)
            self.root.geometry(f"{str(self.client_screen_width)}x{str(self.client_screen_height)}")#tamnhao da janela str"900x800"
            self.root.protocol("WM_DELETE_WINDOW", self.on_close)

            try:
                self.command_socket.connect((SERVER_HOST, COMMAND_PORT))
                print("Conexão com o servidor de comandos estabelecida.")

                time.sleep(0.1)

                self.screen_socket.connect((SERVER_HOST, SCREEN_PORT))
                print("Conexão com o servidor de tela estabelecida.")

                # Substituído pelo uso do ThreadPoolExecutor
                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                    executor.submit(self.receive_screen, self.screen_socket)
                    executor.submit(self.captura_keyborad_e_mouse)
                print("Threads iniciadas.")

            except Exception as e:
                print(f"Erro ao estabelecer conexões: {e}")


import time

def capture_screen(self, FPS=30):
    FRAME_INTERVAL = 1.0 / FPS  # intervalo em segundos

    with mss() as sct:
        # Quadro de referência
        reference_frame = None
        # Contador de quadros
        frame_counter = 0

        while self.running:
            # hora de inicio do quadro
            frame_start_time = time.time()

            # Capture o quadro atual
            screen = sct.grab(sct.monitors[0])

            # Agora o método retorna uma matriz NumPy
            screen_np = self.overlay_cursor_on_screen(screen, (x, y))

            # Aplicamos um filtro de suavização
            screen_np = cv2.GaussianBlur(screen_np, (5, 5), 0)

            # Se ainda não temos um quadro de referência, usamos o primeiro quadro capturado como referência
            if reference_frame is None:
                reference_frame = screen_np
                continue

            # Calculamos a diferença entre o quadro atual e o quadro de referência
            frame_diff = cv2.absdiff(reference_frame, screen_np)

            # Aplicamos um limiar para binarizar a imagem de diferença
            _, threshold_diff = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)

            # Incrementamos o contador de quadros
            frame_counter += 1

            # A cada N quadros, enviamos o quadro completo. Nos outros quadros, enviamos a diferença
            if frame_counter % N == 0:
                frame_data = self.serialize_screen(screen_np)
            else:
                frame_data = self.serialize_screen(threshold_diff)

            self.send_screen(frame_data)

            # Atualizamos o quadro de referência
            reference_frame = screen_np

            # calcule quanto tempo precisamos dormir para manter o FPS desejado
            time_to_next_frame = frame_start_time + FRAME_INTERVAL - time.time()
            # garantindo que time_to_next_frame não é negativo
            time_to_next_frame = max(0, time_to_next_frame)
            # durma pelo tempo necessário
            time.sleep(time_to_next_frame)


janela em foco:
import pyautogui

class MouseEventHandling:
    def __init__(self, conn, server_screen_width, server_screen_height):
        self.conn = conn
        self.server_screen_width = server_screen_width
        self.server_screen_height = server_screen_height
        self.window_name = 'Nome da sua janela tkinter'

    def is_window_in_focus(self):
        active_window = pyautogui.getActiveWindow()
        return active_window and active_window.title == self.window_name

    def on_move(self, x, y):
        if not self.is_window_in_focus():
            return
        # ... o resto do código

    # ... o mesmo para on_click e on_scroll

class KeyboardEventHandling:
    def __init__(self, conn):
        self.conn = conn
        self.pressed_keys = set()
        self.window_name = 'Nome da sua janela tkinter'

    def is_window_in_focus(self):
        active_window = pyautogui.getActiveWindow()
        return active_window and active_window.title == self.window_name

    def on_press(self, key):
        if not self.is_window_in_focus():
            return
        # ... o resto do código

    def on_release(self, key):
        if not self.is_window_in_focus():
            return
        # ... o resto do código
