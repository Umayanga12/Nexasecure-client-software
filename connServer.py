import sys
import os 
import threading
from command import ESP32Device, authenticate_device,GetAuthAddr,GetReqAddr
from gui import prompt_user_password
from logger import setup_logger
from util import ConnectSocketServer, monitor_wallet_status, wait_for_device


serial_lock = threading.Lock()

logger = setup_logger(log_file="logs/connServer.log", log_level="DEBUG")

def handle_server_commands(client_socket, esp_device):
    request_pub_addr = GetReqAddr(esp_device)
    auth_pub_addr = GetAuthAddr(esp_device)
    try:
        while True:
            # Receive command from the socket server
            command = client_socket.recv(1024).decode('utf-8')  # Adjust buffer size as needed
            # if not command:
            #     logger.info("Server closed the connection.")
            #     break

            logger.info(f"Received command from server: {command}")

            # Send the command to the ESP32 device
            esp_device.send_command(command)
            logger.info(f"Sent command to ESP32 device: {command}")

            # Read the response from the ESP32 device
            response = esp_device.read_line()
            logger.info(f"Received response from ESP32 device: {response}")

            # Send the response back to the socket server
            client_socket.sendall(response.encode('utf-8'))
            logger.info(f"Sent response back to server: {response}")

    except Exception as e:
        logger.error(f"Error while handling server commands: {e}")
    finally:
        client_socket.close()
        logger.info("Socket connection closed.")


# ----- Main Application Flow -----
def main():
    # Wait for the SecureWallet (ESP32 device) to be connected
    port = wait_for_device()
    if not port:
        logger.error("Device not found.")
        return

    esp_device = ESP32Device(port)
    remote_server = "127.0.0.1:8080" 
    client_socket = ConnectSocketServer(remote_server=remote_server)
    #print(client_socket)
    # Prompt user for the password using a GUI
    password = prompt_user_password()
    if not password:
        logger.info("No password entered. Exiting.")
        esp_device.close()
        sys.exit(0)

    if authenticate_device(esp_device, password):
        logger.info("Authentication successful.")

        # Start wallet monitor
        #threading.Thread(target=monitor_wallet_status, args=(port, esp_device, client_socket), daemon=True).start()

        # Get public addresses
        requestPubAddr = GetReqAddr(esp_device)
        authpubAddr = GetAuthAddr(esp_device)

        if client_socket:
            try:
                # Send addresses to server
                message = f"{requestPubAddr},{authpubAddr}\n"
                client_socket.sendall(message.encode('utf-8'))
                logger.info(f"Sent to server: {message}")

                # Wait for server validation
                while True:
                    response = client_socket.recv(1024).decode('utf-8')
                    if response.strip() == "VALIDATED":
                        logger.info("Addresses validated by server. Starting communication...")
                        handle_server_commands(client_socket, esp_device)
                        break
                    elif response.strip() == "RETRY":
                        logger.warning("Server requested retry. Waiting for further instructions...")
                    else:
                        logger.warning(f"Server response: {response}. Authentication failed.")
                        break
            except Exception as e:
                logger.error(f"Communication error: {e}")
            finally:
                client_socket.close()
        else:
            logger.error("Could not connect to the socket server.")
    else:
        logger.warning("Authentication failed.")

    esp_device.close()
    logger.info("ESP32 device connection closed.")

    
if __name__ == "__main__":
    main()
