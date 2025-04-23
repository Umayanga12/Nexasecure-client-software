import serial
import time
import sys
import logger
from plyer import notification

# ----- Configuration -----
BAUD_RATE = 115200
READ_TIMEOUT = 1

Wallet_logger = logger.setup_logger("logs/securewallet.log", log_level="DEBUG")

# ----- Serial Port Detection -----
def list_serial_ports():
    """List available serial ports."""
    ports = list(serial.tools.list_ports.comports())
    return ports


def auto_select_port():
    """Attempt to auto-select the ESP32 device by scanning port descriptions."""
    ports = list_serial_ports()
    # Look for common identifiers; adjust the filtering as needed
    for port in ports:
        if "USB" in port.description or "ESP32" in port.description or "CDC" in port.description:
            return port.device
    return None

def check_wallet_online(port) -> bool:
    #print(f"Checking if SecureWallet is online on port {port}...")
    """Check if the SecureWallet device is online by sending a command."""
    while True:
        #print("Thread is running")
        try:
            with serial.Serial(port, BAUD_RATE, timeout=READ_TIMEOUT) as ser:
                time.sleep(2)
                if ser.in_waiting:
                    line = ser.readline().decode(errors="replace").strip()
                    if "Secure Wallet Starting" in line:
                        Wallet_logger.info("Verified SecureWallet startup message.")
                        notification.notify(
                            title="SecureWallet",
                            message="SecureWallet device is ready.",
                            timeout=5
                        )
                        return True
                    else:
                        Wallet_logger.warning("SecureWallet is not online.")
                        return False
                else:
                    Wallet_logger.warning("Device did not send the expected startup message.")
                    return False
        except Exception as e:
            Wallet_logger.error(f"Error reading from port {port}: {e}")
            return False

        time.sleep(2)


def monitor_wallet_status(port, esp_device):
    """Monitor the secure wallet status and handle authentication."""
    consecutive_failures = 0
    max_failures = 5
    while True:
        if check_wallet_online(port):
            Wallet_logger.info("SecureWallet is online.")
            consecutive_failures = 0
            esp_device.send_command("GET_STATUS")
        else:
            consecutive_failures += 1
            Wallet_logger.warning(f"Failed to connect to SecureWallet. Attempt {consecutive_failures}/{max_failures}")
            if consecutive_failures >= max_failures:
                Wallet_logger.error("Max failures reached. Exiting...")
                logger.error("Wallet offline for too long. Disconnecting user from the server.")
                esp_device.close()
                sys.exit(1)
        time.sleep(2)


def wait_for_device():
    """Loop until the SecureWallet device is detected and return its port."""
    Wallet_logger.info("Waiting for SecureWallet device to be plugged in...")
    while True:
        port = auto_select_port()
        if port:
            Wallet_logger.info(f"Detected device on port: {port}")
            notification.notify(
                title="SecureWallet",
                message="SecureWallet device detected. Please wait...",
                timeout=5
            )
            return port
        else:
            time.sleep(2)
