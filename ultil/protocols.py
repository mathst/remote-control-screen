import logging
import time

def send(socket, msg, retry_count=3):
    total_sent = 0
    while total_sent < len(msg):
        try:
            remaining_data = msg[total_sent:]
            sent = socket.send(remaining_data)

            if sent == 0:
                raise RuntimeError("Socket connection broken")

            total_sent += sent
        except (ConnectionResetError, BrokenPipeError):
            if retry_count > 0:
                logging.warning("Connection issues. Retrying...")
                time.sleep(2)  # sleep for 2 seconds before retrying
                retry_count -= 1
                continue
            else:
                logging.error("Connection issues persist after retries. Closing connection.")
                socket.close()
                break
        except Exception as e:
            logging.error(f"An error occurred while sending data: {e}")
            break
    return total_sent == len(msg)

def receive(socket, length, retry_count=3):
    try:
        received_data = b""
        bytes_recd = 0
        while bytes_recd < length:
            remaining_length = length - bytes_recd
            chunk = socket.recv(min(remaining_length, 8192))

            if chunk == b'':
                raise RuntimeError("Socket connection broken")

            received_data += chunk
            bytes_recd += len(chunk)
        if bytes_recd != length:
            raise RuntimeError("Incomplete data received")
        return received_data
    except (ConnectionResetError, BrokenPipeError):
        if retry_count > 0:
            logging.warning("Connection issues. Retrying...")
            time.sleep(2)  # sleep for 2 seconds before retrying
            retry_count -= 1
            return receive(socket, length, retry_count)  # Return the value from the retry
        else:
            logging.error("Connection issues persist after retries. Closing connection.")
            socket.close()
            return None
    except Exception as e:
        logging.error(f"An error occurred while receiving data: {e}")
        return None
