import random
import socket
import string
import threading
import time
import uuid

# Constantes
Port = 6651
ProcessingSlack = 2
MAIN_SOCKET_PREFIX = "<Main>"
DESKTOP_SOCKET_PREFIX = "<Desktop>"
KEYBOARD_SOCKET_PREFIX = "<Keyboard>"
FILES_SOCKET_PREFIX = "<Files>"
ERROR_LOG_START = "<<ERROR>"
ERROR_LOG_END = "<ERROR>"

# Dicionário para armazenar as conexões dos clientes
connections = {}

# Classe para definir o tipo de conexão
class ConnectionType:
    Main = 1
    Desktop = 2
    Keyboard = 3
    Files = 4

# Função para gerar um ID único
def generate_id():
    return str(uuid.uuid4())

def generate_password():
    password_length = 8
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(password_length))

def check_id_exists(connections, ID):
    return any(item[2] == ID for item in connections.values())

def get_list_item_ID(connections, ID):
    return next((item for item in connections.values() if item[2] == ID), None)

def update_list_item(connections, ID, index, value):
    item = get_list_item_ID(connections, ID)
    if item is not None:
        item[index] = value

def insert_target_ID(connections, main_socket, target_id, id):
    item = get_list_item_ID(connections, str(main_socket.Handle))
    item2 = get_list_item_ID(connections, target_id)
    if item is not None and item2 is not None:
        item[3] = target_id
        item2[3] = id

def update_target_id(connections, ID, TargetID):
    item = get_list_item_ID(connections, ID)
    item2 = get_list_item_ID(connections, TargetID)
    if item is not None and item2 is not None:
        return item[2], item2[2]
    else:
        return ID, TargetID

def check_id_password(items, id, password):
    return any(item[1] == id and item[2] == password for item in items)

class TThreadConnectionDefine(threading.Thread):
    def __init__(self, socket, connections):
        super().__init__()
        self.define_socket = socket
        self.connections = connections

    def run(self):
        while True:
            time.sleep(ProcessingSlack)

            if self.define_socket is None or not self.define_socket.Connected:
                break

            if self.define_socket.ReceiveLength < 1:
                continue

            buffer = self.define_socket.ReceiveText()

            position = buffer.find(MAIN_SOCKET_PREFIX)
            if position > 0:
                self.create_main_thread()
                break

            position = buffer.find(DESKTOP_SOCKET_PREFIX)
            if position > 0:
                id = self.extract_id(buffer, DESKTOP_SOCKET_PREFIX)
                self.create_thread(TThreadConnectionDesktop, id)
                break

            position = buffer.find(KEYBOARD_SOCKET_PREFIX)
            if position > 0:
                id = self.extract_id(buffer, KEYBOARD_SOCKET_PREFIX)
                self.create_thread(TThreadConnectionKeyboard, id)
                break

            position = buffer.find(FILES_SOCKET_PREFIX)
            if position > 0:
                id = self.extract_id(buffer, FILES_SOCKET_PREFIX)
                self.create_thread(TThreadConnectionFiles, id)
                break

    def create_main_thread(self):
        thread_main = TThreadConnectionMain(self.define_socket, self.connections)
        thread_main.start()

    def create_thread(self, thread_class, id):
        thread = thread_class(self.define_socket, id, self.connections)
        thread.start()

    def extract_id(self, buffer, prefix):
        position = buffer.find(prefix)
        buffer_temp = buffer[position + len(prefix):]
        id = buffer_temp.split('<')[0]
        return id

class TThreadConnectionBase(threading.Thread):
    def __init__(self, socket, id, connections):
        super().__init__()
        self.socket = socket
        self.id = id
        self.connections = connections

    def send_text(self, text):
        while self.socket.SendText(text) < 0:
            time.sleep(ProcessingSlack)

class TThreadConnectionMain(TThreadConnectionBase):
    def __init__(self, socket, connections):
        super().__init__(socket, None, connections)
        self.ID = None
        self.Password = None
        self.TargetID = None
        self.TargetPassword = None

    def add_items(self):
        self.ID = generate_id()
        self.Password = generate_password()
        item_data = [
            self.socket.Handle,
            self.socket.RemoteAddress,
            self.ID,
            self.Password,
            '',
            'Calculating...'
        ]
        self.connections[self.socket.Handle] = item_data

    def run(self):
        self.add_items()
        self.send_text(f'{MAIN_SOCKET_PREFIX}<{self.ID}><|><{self.Password}>')

        while True:
            time.sleep(ProcessingSlack)

            if self.socket is None or not self.socket.Connected:
                break

            if self.socket.ReceiveLength < 1:
                continue

            buffer = self.socket.ReceiveText()

            position = buffer.find(DESKTOP_SOCKET_PREFIX)
            if position > 0:
                self.process_socket(buffer, DESKTOP_SOCKET_PREFIX)
                break

            position = buffer.find(KEYBOARD_SOCKET_PREFIX)
            if position > 0:
                self.process_socket(buffer, KEYBOARD_SOCKET_PREFIX)
                break

            position = buffer.find(FILES_SOCKET_PREFIX)
            if position > 0:
                self.process_files_socket(buffer)
                break

    def process_socket(self, buffer, prefix):
        position = buffer.find(prefix)
        buffer_temp = buffer[position + len(prefix):]
        position = buffer_temp.find('<')
        target_id = buffer_temp[:position]
        if check_id_exists(self.connections, target_id):
            target_item = get_list_item_ID(self.connections, target_id)
            if target_item is not None and target_item[3] == '':
                self.send_text('<|IDEXISTS!REQUESTPASSWORD|>')
            else:
                self.send_text('')
        else:
            self.send_text('')

    def process_files_socket(self, buffer):
        position = buffer.find(FILES_SOCKET_PREFIX)
        buffer_temp = buffer[position + len(FILES_SOCKET_PREFIX):]
        position = buffer_temp.find('<')
        id = buffer_temp[:position]
        buffer_temp = buffer_temp[position + 2:]
        position = buffer_temp.find('<')
        target_id = buffer_temp[:position]
        self.ID, self.TargetID = update_target_id(self.connections, id, target_id)

        # Relates the main Sockets
        main_socket_item = get_list_item_ID(self.connections, self.ID)
        target_main_socket_item = get_list_item_ID(self.connections, self.TargetID)
        if main_socket_item is not None and target_main_socket_item is not None:
            main_socket_item[0] = target_main_socket_item[0]
            target_main_socket_item[0] = main_socket_item[0]
        # Relates the Remote Desktop
        main_desktop_socket_item = get_list_item_ID(self.connections, self.ID)
        target_desktop_socket_item = get_list_item_ID(self.connections, self.TargetID)
        if main_desktop_socket_item is not None and target_desktop_socket_item is not None:
            main_desktop_socket_item[1] = target_desktop_socket_item[1]
            target_desktop_socket_item[1] = main_desktop_socket_item[1]
        # Relates the Keyboard Socket
        main_keyboard_socket_item = get_list_item_ID(self.connections, self.ID)
        target_keyboard_socket_item = get_list_item_ID(self.connections, self.TargetID)
        if main_keyboard_socket_item is not None and target_keyboard_socket_item is not None:
            main_keyboard_socket_item[2] = target_keyboard_socket_item[2]
        # Relates the Share Files
        main_files_socket_item = get_list_item_ID(self.connections, self.ID)
        target_files_socket_item = get_list_item_ID(self.connections, self.TargetID)
        if main_files_socket_item is not None and target_files_socket_item is not None:
            main_files_socket_item[3] = target_files_socket_item[3]
            target_files_socket_item[3] = main_files_socket_item[3]
        # Warns Access
        main_main_socket_item = get_list_item_ID(self.connections, self.ID)
        if main_main_socket_item is not None:
            main_main_socket_item[0].SendText('')
        # Get first screenshot
        main_desktop_socket_item = get_list_item_ID(self.connections, self.ID)
        if main_desktop_socket_item is not None:
            main_desktop_socket_item[1].SendText('')

        # Stop relations
        if ERROR_LOG_START in buffer:
            self.send_text('')
            target_main_socket_item = get_list_item_ID(self.connections, self.TargetID)
            if target_main_socket_item is not None:
                target_main_socket_item[0].SendText('')
                target_main_socket_item[0] = None
            update_list_item(self.connections, self.ID, 3, '')
            update_list_item(self.connections, self.TargetID, 3, '')

        # Redirect commands
        if ERROR_LOG_END in buffer:
            buffer_temp = buffer_temp[position + len(ERROR_LOG_END):]
            target_main_socket_item = get_list_item_ID(self.connections, self.TargetID)
            if target_main_socket_item is not None and target_main_socket_item[0] is not None and target_main_socket_item[0].Connected:
                while target_main_socket_item[0].SendText(buffer_temp) < 0:
                    time.sleep(ProcessingSlack)

class TThreadConnectionDesktop(threading.Thread):
    def __init__(self, socket, my_id, connections):
        super().__init__()
        self.desktop_socket = socket
        self.my_id = my_id
        self.connections = connections

    def run(self):
        while True:
            time.sleep(ProcessingSlack)

            if self.desktop_socket is None or not self.desktop_socket.Connected:
                break

            if self.desktop_socket.ReceiveLength < 1:
                continue

            buffer = self.desktop_socket.ReceiveText()

            for connection_id, connection_data in self.connections.items():
                main_socket, desktop_socket, keyboard_socket, files_socket, _, _ = connection_data
                if main_socket is not None and main_socket.targetMainSocket is not None and main_socket.targetMainSocket.Connected:
                    while main_socket.targetMainSocket.SendText(buffer) < 0:
                        time.sleep(ProcessingSlack)


class TThreadConnectionKeyboard(threading.Thread):
    def __init__(self, socket, my_id, connections):
        super().__init__()
        self.keyboard_socket = socket
        self.my_id = my_id
        self.connections = connections

    def run(self):
        while True:
            time.sleep(ProcessingSlack)

            if self.keyboard_socket is None or not self.keyboard_socket.Connected:
                break

            if self.keyboard_socket.ReceiveLength < 1:
                continue

            buffer = self.keyboard_socket.ReceiveText()

            for connection_id, connection_data in self.connections.items():
                main_socket, desktop_socket, keyboard_socket, files_socket, _, _ = connection_data
                if main_socket is not None and main_socket.targetMainSocket is not None and main_socket.targetMainSocket.Connected:
                    while main_socket.targetMainSocket.SendText(buffer) < 0:
                        time.sleep(ProcessingSlack)


class TThreadConnectionFiles(threading.Thread):
    def __init__(self, socket, my_id, connections):
        super().__init__()
        self.files_socket = socket
        self.my_id = my_id
        self.connections = connections

    def run(self):
        while True:
            time.sleep(ProcessingSlack)

            if self.files_socket is None or not self.files_socket.Connected:
                break

            if self.files_socket.ReceiveLength < 1:
                continue

            buffer = self.files_socket.ReceiveText()

            for connection_id, connection_data in self.connections.items():
                main_socket, desktop_socket, keyboard_socket, files_socket, _, _ = connection_data
                if main_socket is not None and main_socket.targetMainSocket is not None and main_socket.targetMainSocket.Connected:
                    while main_socket.targetMainSocket.SendText(buffer) < 0:
                        time.sleep(ProcessingSlack)



class TThreadPingTimer(threading.Thread):
    def __init__(self, connections):
        super().__init__()
        self.connections = connections

    def run(self):
        while True:
            time.sleep(1)
            for connection_id, connection_data in self.connections.items():
                main_socket, _, _, _, _, _ = connection_data
                if main_socket is not None and main_socket.Connected:
                    main_socket.SendText('')
                    start_ping = time.time()
                    while main_socket.SendText(f'{int((time.time() - start_ping) * 1000)}') < 0:
                        time.sleep(ProcessingSlack)


                        
                        
'''
Aqui está uma versão mais detalhada do documento:

Visão Geral do Código:

O programa foi desenvolvido utilizando uma arquitetura baseada em threads para lidar com várias conexões de clientes simultaneamente. Cada conexão é gerenciada por uma thread específica, responsável por uma funcionalidade específica, como a conexão principal, área de trabalho remota, teclado remoto e compartilhamento de arquivos.

Detalhamento das Threads de Conexão:

1. TThreadConnection_Define:
   - Essa thread é responsável por identificar o tipo de conexão com base nos dados recebidos do cliente.
   - Ela cria uma instância da thread de conexão apropriada com base no tipo identificado.

2. TThreadConnection_Main:
   - Essa thread lida com a conexão principal de cada cliente.
   - Cada cliente que se conecta ao servidor recebe uma instância dessa thread.
   - A conexão principal envolve autenticação e redirecionamento de comandos para outras conexões.
   - Ela mantém uma referência para o socket de comunicação principal (mainSocket).
   - Possui referências para outras threads de conexão, como TThreadConnection_Desktop, TThreadConnection_Keyboard e TThreadConnection_Files.
   - O thread principal (Tfrm_Main) armazena as informações de cada conexão principal no ListView.

3. TThreadConnection_Desktop, TThreadConnection_Keyboard, TThreadConnection_Files:
   - Cada uma dessas threads lida com uma funcionalidade específica (área de trabalho remota, teclado remoto e compartilhamento de arquivos).
   - Elas recebem e enviam dados relacionados a essa funcionalidade entre o cliente e o destino apropriado.
   - Essas threads mantêm referências para os sockets de comunicação específicos (desktopSocket, keyboardSocket, filesSocket).
   - As conexões de área de trabalho remota e teclado remoto possuem uma referência adicional para o socket de comunicação do cliente de destino (targetDesktopSocket, targetKeyboardSocket).
   - As threads de conexão de área de trabalho remota (TThreadConnection_Desktop) e compartilhamento de arquivos (TThreadConnection_Files) também têm referências cruzadas para permitir a comunicação entre os clientes.

Detalhes sobre Sockets e Comunicação:

O servidor utiliza o componente TServerSocket para aguardar conexões de clientes em uma porta específica. Quando um cliente se conecta, um novo soquete (socket) é criado para essa conexão e um objeto de thread de conexão é associado a esse soquete. A comunicação entre o servidor e os clientes é realizada por meio de envio e recebimento de dados pelos sockets.

Autenticação:
- A conexão principal (TThreadConnection_Main) é responsável por autenticar os clientes.
- A autenticação é feita por meio de um ID único gerado para cada cliente e uma senha associada a esse ID.
- O programa utiliza as funções GenerateID e GeneratePassword para gerar IDs e senhas aleatórias.
- A conexão principal verifica se o ID fornecido pelo cliente está presente na lista de conexões estabelecidas e se a senha fornecida corresponde à senha associada a esse ID.

Ping:
- O temporizador (Ping_Timer) é responsável por enviar pings regulares aos clientes conectados.
- Esses pings são utilizados para verificar a conectividade e calcular o tempo de resposta.
- As informações de ping são exibidas no ListView, permitindo monitorar a latência da conexão com cada cliente.

Manipulação de Erros:
- O programa inclui o procedimento RegisterErrorLog, responsável por registrar erros em um log de erros no Memo.
- Esse log de erros pode ser útil para depuração e monitoramento de problemas no servidor.
- As informações registradas incluem um cabeçalho, a classe de erro e a mensagem de erro.

Além dessas funcionalidades e threads principais, o código também possui funções auxiliares, como GetAppVersionStr para obter a versão do aplicativo, e funções como FindListItemID, CheckIDExists e CheckIDPassword para auxiliar na manipulação dos dados na ListView.

Essa visão geral detalhada do código deve auxiliar o programador na compreensão e implementação do sistema. No entanto, é importante lembrar que a documentação completa e detalhada, incluindo todas as funcionalidades, estruturas de dados e fluxos de trabalho específicos, seria mais adequada para guiar o processo de desenvolvimento do sistema.'''
