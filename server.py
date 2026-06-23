from flask import Flask, render_template, request, jsonify
import json
import os
import hashlib
from web3 import Web3
from eth_account import Account

app = Flask(__name__, template_folder='templates')

USER_DB_FILE = "users.json"

def load_users():
    if os.path.exists(USER_DB_FILE):
        try:
            with open(USER_DB_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_users(users):
    with open(USER_DB_FILE, "w") as f:
        json.dump(users, f, indent=4)

def get_web3_and_contract():
    if not os.path.exists("config.json") or not os.path.exists("contract_data.json"):
        return None, None, None
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        with open("contract_data.json", "r") as f:
            contract_data = json.load(f)
            
        rpc_url = config.get("rpc_url")
        contract_address = config.get("contract_address")
        abi = contract_data.get("abi")
        
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        if not w3.is_connected():
            return None, None, None
            
        contract = w3.eth.contract(address=contract_address, abi=abi)
        return w3, contract, config
    except Exception:
        return None, None, None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status', methods=['GET'])
def get_node_status():
    w3, _, config = get_web3_and_contract()
    if not w3:
        return jsonify({
            "connected": False,
            "message": "Node Ethereum Lokal (Ganache/Anvil) tidak terdeteksi. Silakan jalankan node lokal dan deploy contract."
        })
    return jsonify({
        "connected": True,
        "rpc_url": config["rpc_url"],
        "contract_address": config["contract_address"],
        "owner_address": config["owner_address"],
        "latest_block": w3.eth.block_number
    })

@app.route('/api/register', methods=['POST'])
def register():
    w3, contract, config = get_web3_and_contract()
    if not w3:
        return jsonify({"success": False, "message": "Koneksi node terputus!"}), 503
        
    data = request.json
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return jsonify({"success": False, "message": "Email dan password diperlukan!"}), 400
        
    users = load_users()
    if email in users:
        return jsonify({"success": False, "message": "Email sudah terdaftar!"}), 400
        
    # Calculate hash locally at backend (mirroring front-end client-side logic)
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    # 1. Generate Wallet
    new_wallet = Account.create()
    user_address = new_wallet.address
    user_private_key = new_wallet.key.hex()
    
    # 2. Fund ETH from Owner for Gas Fee
    owner_address = config["owner_address"]
    try:
        tx_hash_eth = w3.eth.send_transaction({
            'from': owner_address,
            'to': user_address,
            'value': w3.to_wei(1.0, 'ether')
        })
        w3.eth.wait_for_transaction_receipt(tx_hash_eth)
    except Exception as e:
        return jsonify({"success": False, "message": f"Gagal mentransfer Gas Fee ETH: {str(e)}"}), 500
        
    # 3. Mint Pebri Coins (100 koin)
    try:
        tx_hash_mint = contract.functions.mint(user_address, 100).transact({'from': owner_address})
        w3.eth.wait_for_transaction_receipt(tx_hash_mint)
    except Exception as e:
        return jsonify({"success": False, "message": f"Gagal mencetak Pebri Coin: {str(e)}"}), 500
        
    # 4. Save to mock DB
    users[email] = {
        "password_hash": password_hash,
        "address": user_address,
        "private_key": user_private_key
    }
    save_users(users)
    
    return jsonify({
        "success": True,
        "address": user_address,
        "private_key": user_private_key,
        "tx_hash_eth": tx_hash_eth.hex(),
        "tx_hash_mint": tx_hash_mint.hex()
    })

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return jsonify({"success": False, "message": "Email dan password diperlukan!"}), 400
        
    users = load_users()
    if email not in users:
        return jsonify({"success": False, "message": "Email belum terdaftar!"}), 404
        
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    user_data = users[email]
    
    if user_data["password_hash"] != password_hash:
        return jsonify({"success": False, "message": "Password salah!"}), 401
        
    return jsonify({
        "success": True,
        "email": email,
        "address": user_data["address"],
        "private_key": user_data["private_key"]
    })

@app.route('/api/state', methods=['GET'])
def get_state():
    w3, contract, config = get_web3_and_contract()
    if not w3:
        return jsonify({"success": False, "message": "Koneksi node terputus!"}), 503
        
    user_address = request.args.get("user_address")
    if not user_address:
        return jsonify({"success": False, "message": "Address user diperlukan!"}), 400
        
    try:
        user_coin_bal = contract.functions.balanceOf(user_address).call()
        user_eth_bal = w3.from_wei(w3.eth.get_balance(user_address), 'ether')
        
        owner_address = config["owner_address"]
        owner_coin_bal = contract.functions.balanceOf(owner_address).call()
        owner_eth_bal = w3.from_wei(w3.eth.get_balance(owner_address), 'ether')
        
        product_name = contract.functions.productName().call()
        product_price = contract.functions.productPrice().call()
        product_stock = contract.functions.productStock().call()
        
        return jsonify({
            "success": True,
            "latest_block": w3.eth.block_number,
            "user_coin_bal": int(user_coin_bal),
            "user_eth_bal": float(user_eth_bal),
            "owner_address": owner_address,
            "owner_coin_bal": int(owner_coin_bal),
            "owner_eth_bal": float(owner_eth_bal),
            "product_name": product_name,
            "product_price": int(product_price),
            "product_stock": int(product_stock)
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Gagal membaca blockchain: {str(e)}"}), 500

@app.route('/api/buy', methods=['POST'])
def buy():
    w3, contract, _ = get_web3_and_contract()
    if not w3:
        return jsonify({"success": False, "message": "Koneksi node terputus!"}), 503
        
    data = request.json
    user_address = data.get("user_address")
    private_key = data.get("private_key")
    quantity = int(data.get("quantity", 1))
    
    if not user_address or not private_key:
        return jsonify({"success": False, "message": "Kredensial transaksi tidak lengkap!"}), 400
        
    try:
        # Build transaction payload
        nonce = w3.eth.get_transaction_count(user_address)
        tx = contract.functions.beliBarang(quantity).build_transaction({
            'from': user_address,
            'nonce': nonce,
            'gas': 250000,
            'gasPrice': w3.eth.gas_price
        })
        
        # Local signing
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
        
        # Broadcast raw transaction
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        # Wait receipt
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return jsonify({
            "success": True,
            "tx_hash": tx_hash.hex(),
            "block_number": tx_receipt.blockNumber,
            "gas_used": tx_receipt.gasUsed
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Gagal memproses pembelian: {str(e)}"}), 500

if __name__ == '__main__':
    print("Membuka server Flask edukasi Web3...")
    app.run(host='0.0.0.0', port=5000, debug=True)
