import zlib
import win32clipboard
import os
import threading
import socket
import struct
from ctypes import windll
from PIL import ImageGrab
from io import BytesIO
from queue import Queue

# Definições de variáveis
ProcessingSlack = 10
ResolutionWidth = 0
ResolutionHeight = 0
Lock = threading.Lock()

# Funções auxiliares
def GetScreenToMemoryStream(include_cursor=True, stream=None):
    try:
        if stream is None:
            stream = BytesIO()

        screenshot = ImageGrab.grab(include_layered_windows=True, all_screens=True)
        screenshot.save(stream, format="PNG")
        return stream
    except Exception as e:
        print("Erro na captura de tela:", e)
        return None

def CompressStreamWithZLib(input_stream):
    compressor = zlib.compressobj(9, zlib.DEFLATED, zlib.MAX_WBITS | 16)
    compressed_data = compressor.compress(input_stream.read())
    compressed_data += compressor.flush()
    input_stream.seek(0)
    input_stream.truncate(0)
    input_stream.write(compressed_data)

def DeCompressStreamWithZLib(input_stream):
    decompressor = zlib.decompressobj(zlib.MAX_WBITS | 16)
    decompressed_data = decompressor.decompress(input_stream.read())
    input_stream.seek(0)
    input_stream.truncate(0)
    input_stream.write(decompressed_data)

def CompareStream(stream1, stream2, result_stream):
    stream1.seek(0)
    stream2.seek(0)
    result_stream.seek(0)

    while True:
        byte1 = stream1.read(1)
        byte2 = stream2.read(1)

        if not byte1 or not byte2:
            break

        if byte1 == byte2:
            result_stream.write(b'\x00')
        else:
            result_stream.write(b'\x01')

def SendDataToServer(data):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("192.168.0.1", 1234))  # Substitua pelo endereço IP e porta do servidor
        s.sendall(data)
        s.close()
    except Exception as e:
        print("Erro ao enviar dados para o servidor:", e)

def WorkerThread():
    global ResolutionWidth, ResolutionHeight

    while True:
        try:
            # Substitua a lógica de captura de tela por uma função apropriada em Python
            stream = BytesIO()
            GetScreenToMemoryStream(True, stream)
            compressed_data = CompressStreamWithZLib(stream)
            if compressed_data:
                SendDataToServer(compressed_data)
                stream.close()

        except Exception as e:
            print("Erro na thread:", e)

def main():
    try:
        # Defina a largura e altura da resolução do monitor corretamente
        user32 = windll.user32
        ResolutionWidth = user32.GetSystemMetrics(0)
        ResolutionHeight = user32.GetSystemMetrics(1)

        thread_count = 5  # Número de threads de trabalho
        threads = []

        for _ in range(thread_count):
            thread = threading.Thread(target=WorkerThread)
            thread.daemon = True
            threads.append(thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

    except Exception as e:
        print("Erro no programa principal:", e)

if __name__ == "__main__":
    main()


                elif buffertpm :
                    print("Matching data:", buffertpm)
                    match buffertpm:
                        case '<|PING|>':
                            self.handle_ping(buffertpm)
                        case '<|SETPING|>':
                            self.set_ping(buffertpm)
                        case '<|ACCESSING|>':
                            self.handle_warns_access_and_remove_wallpaper(buffertpm)
                        case '<|IDEXISTS!REQUESTPASSWORD|>':
                            self.handle_id_exists_request_password(buffertpm)
                        case '<|IDNOTEXISTS|>':
                            self.handle_id_not_exists(buffertpm)
                        case '<|ACCESSDENIED|>':
                            self.handle_wrong_password(buffertpm)
                        case '<|ACCESSBUSY|>':
                            self.handle_pc_busy(buffertpm)
                        case '<|ACCESSGRANTED|>':
                            self.handle_access_granted(buffertpm)
                        case '<|DISCONNECTED|>':
                            self.handle_lost_connection_to_pc(buffertpm)
