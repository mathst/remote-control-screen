import logging
import select
import socket
import time
import zlib
import msgpack
from ultil.protocols import receive, send
from ultil.constant import SPECIAL_BUFFER_SIZE


class SocketConnection:
    def __init__(self, host, send_port=None, recv_port=None, retry_count=3):
        self.command_socket = None
        self.screen_socket = None
        self.host = host
        self.send_port = send_port
        self.recv_port = recv_port
        self.retry_count = retry_count

    def establish_connection(self):
        try:
            if self.send_port:
                self.command_socket = self.connect_to_server(self.host, self.send_port, self.retry_count)
                logging.info(f"Connected to command server: {self.host}:{self.send_port}")
            if self.recv_port:
                self.screen_socket = self.connect_to_server(self.host, self.recv_port, self.retry_count)
                logging.info(f"Connected to screen server: {self.host}:{self.recv_port}")
                
        except BlockingIOError:
            # Esperar até que a conexão seja estabelecida
            _, writable, _ = select.select([], [self.command_socket, self.screen_socket], [])
            if self.command_socket in writable or self.screen_socket in writable:
                pass
        except ConnectionRefusedError as e:
            logging.error(f"Connection refused. Make sure the server is running and the IP and port are correct: {e}")
            raise
        except Exception as e:
            logging.error(f"Connection error: {e}")
            raise

    def close_connection(self):
        if self.command_socket:
            self.command_socket.close()
        if self.screen_socket:
            self.screen_socket.close()

    def start_listening_c(self, backlog=1):
        if self.screen_socket is None:
            try:
                self.screen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.screen_socket.bind((self.host, self.recv_port))
                self.screen_socket.listen(backlog)
                logging.info(f"Screen server is listening on {self.host}:{self.recv_port}")
            except Exception as e:
                logging.error(f"Error while starting screen server: {e}")
                raise
        else:
            logging.warning(f"Screen socket is already listening on {self.host}:{self.recv_port}")

    def connect_to_server(self, host, port, retry_count):
        for _ in range(retry_count):
            try:
                socket_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socket_obj.connect((host, port))
                logging.info(f"Connected to server: {host}:{port}")
                return socket_obj
            except ConnectionRefusedError:
                logging.warning("Connection refused. Retrying in 5 seconds...")
                time.sleep(5)
        logging.error("Could not connect to the server after multiple attempts.")
        return None

    def send(self, data):
        if self.command_socket:
            try:
                serialized_data = msgpack.packb(data)
                logging.debug(f"Data size before compression: {len(serialized_data)} bytes")
                compressed_data = zlib.compress(serialized_data)
                logging.debug(f"Data size after compression: {len(compressed_data)} bytes")
                send(self.command_socket, compressed_data)
                logging.debug(f"Sent data: {data}")
            except socket.error as e:
                logging.error(f"Socket error while sending data: {e}")
                self.command_socket = None  # Close the socket and set it to None
            except Exception as e:
                logging.error(f"Error while sending data: {e}")
                raise


    def recv(self, data_size):
        if self.screen_socket:
            try:
                data = receive(self.screen_socket, data_size)
                if data is not None:
                    logging.debug(f"Received data size: {len(data)} bytes")
                    decompressed_data = zlib.decompress(data)
                    logging.debug(f"Decompressed data size: {len(decompressed_data)} bytes")
                    deserialized_data = msgpack.unpackb(decompressed_data, raw=False)
                    logging.debug(f"Received data: {deserialized_data}")
                    return deserialized_data
                else:
                    logging.warning("No data received")
            except socket.error as e:
                logging.error(f"Socket error while receiving data: {e}")
                self.screen_socket = None  # Close the socket and set it to None
            except Exception as e:
                logging.error(f"Error while receiving data: {e}")
                raise
