from flask import Flask, request, jsonify
import sys
from logger import setup_logger
from command import *

# Initialize the logger
logger = setup_logger(log_file="logs/securewalletOpr.log", log_level="DEBUG")

# Initialize the ESP32 device
# Replace '/dev/ttyUSB0' with the appropriate serial port for your system
device = ESP32Device('/dev/ttyUSB0')

app = Flask(__name__)

@app.route('/authenticate', methods=['POST'])
def authenticate():
    data = request.json
    password = data.get('password')
    if not password:
        return jsonify({"error": "Password is required"}), 400
    success = authenticate_device(device, password)
    if success:
        return jsonify({"message": "Authentication successful"}), 200
    else:
        return jsonify({"error": "Authentication failed"}), 401

@app.route('/logout', methods=['POST'])
def logout():
    success = logout_device(device)
    if success:
        return jsonify({"message": "Logged out successfully"}), 200
    else:
        return jsonify({"error": "Logout failed"}), 500

@app.route('/getreqnft', methods=['GET'])
def get_req_nft():
    response = getreqnft(device)
    if response:
        return jsonify({"nft": response}), 200
    else:
        return jsonify({"error": "Failed to get NFT request"}), 500

@app.route('/getauthnft', methods=['GET'])
def get_auth_nft():
    response = getauthnft(device)
    if response:
        return jsonify({"nft": response}), 200
    else:
        return jsonify({"error": "Failed to get NFT auth"}), 500

@app.route('/setreqnft', methods=['POST'])
def set_req_nft():
    data = request.json
    nft = data.get('nft')
    if not nft:
        return jsonify({"error": "NFT is required"}), 400
    response = setreqnft(device, nft)
    if response:
        return jsonify({"message": response}), 200
    else:
        return jsonify({"error": "Failed to set NFT request"}), 500

@app.route('/setauthnft', methods=['POST'])
def set_auth_nft():
    data = request.json
    nft = data.get('nft')
    if not nft:
        return jsonify({"error": "NFT is required"}), 400
    response = setauthnft(device, nft)
    if response:
        return jsonify({"message": response}), 200
    else:
        return jsonify({"error": "Failed to set NFT auth"}), 500

@app.route('/signauthnft', methods=['POST'])
def sign_auth_nft():
    data = request.json
    msg = data.get('msg')
    if not msg:
        return jsonify({"error": "Message is required"}), 400
    response = signauthnft(device, msg)
    if response:
        return jsonify({"signature": response}), 200
    else:
        return jsonify({"error": "Failed to sign NFT auth"}), 500

@app.route('/signreqnft', methods=['POST'])
def sign_req_nft():
    data = request.json
    msg = data.get('msg')
    if not msg:
        return jsonify({"error": "Message is required"}), 400
    response = Signreqnft(device, msg)
    if response:
        return jsonify({"signature": response}), 200
    else:
        return jsonify({"error": "Failed to sign NFT request"}), 500

@app.route('/removereqnft', methods=['POST'])
def remove_req_nft():
    response = remove_req_nft(device)
    if response:
        return jsonify({"message": response}), 200
    else:
        return jsonify({"error": "Failed to remove NFT request"}), 500

@app.route('/removeauthnft', methods=['POST'])
def remove_auth_nft():
    response = remove_auth_nft(device)
    if response:
        return jsonify({"message": response}), 200
    else:
        return jsonify({"error": "Failed to remove NFT auth"}), 500

@app.route('/getreqaddr', methods=['GET'])
def get_req_addr():
    response = get_req_addr(device)
    if response:
        return jsonify({"address": response}), 200
    else:
        return jsonify({"error": "Failed to get request address"}), 500

@app.route('/getauthaddr', methods=['GET'])
def get_auth_addr():
    response = get_auth_addr(device)
    if response:
        return jsonify({"address": response}), 200
    else:
        return jsonify({"error": "Failed to get auth address"}), 500

