import json
import os
import sys

def main():
    # Make sure we have web3 installed
    try:
        from web3 import Web3
    except ImportError:
        print("Installing web3.py...")
        os.system(f"{sys.executable} -m pip install web3")
        from web3 import Web3

    # Check for contract data
    if not os.path.exists("contract_data.json"):
        print("Error: contract_data.json not found. Run compile_contract.py first!")
        sys.exit(1)

    with open("contract_data.json", "r") as f:
        contract_data = json.load(f)

    abi = contract_data["abi"]
    bytecode = contract_data["bytecode"]

    # Local nodes commonly run on 8545 (Anvil/Hardhat) or 7545 (Ganache GUI) or 8545 (Ganache CLI)
    rpc_urls = [
        "http://127.0.0.1:8545",  # Anvil / Hardhat / Ganache CLI
        "http://127.0.0.1:7545",  # Ganache GUI
    ]

    w3 = None
    connected_url = None
    for url in rpc_urls:
        try:
            temp_w3 = Web3(Web3.HTTPProvider(url))
            if temp_w3.is_connected():
                w3 = temp_w3
                connected_url = url
                break
        except Exception:
            continue

    if not w3:
        print("="*60)
        print("ERROR: Tidak dapat terhubung ke Ethereum Node lokal.")
        print("Silakan jalankan Ganache, Anvil (Foundry), atau Hardhat Node terlebih dahulu.")
        print("Perintah untuk menjalankan Node lokal:")
        print("  - Ganache CLI: npx ganache-cli")
        print("  - Anvil (Foundry): anvil")
        print("  - Hardhat Node: npx hardhat node")
        print("="*60)
        sys.exit(1)

    print(f"Terhubung ke Ethereum Node lokal di {connected_url}")

    # Set deployer account (usually account 0 in Ganache/Anvil)
    try:
        accounts = w3.eth.accounts
        if not accounts:
            print("Error: Tidak ada akun yang tersedia di Ethereum Node.")
            sys.exit(1)
        
        deployer = accounts[0]
        w3.eth.default_account = deployer
    except Exception as e:
        print(f"Error mengambil daftar akun: {e}")
        sys.exit(1)
        
    print(f"Address Deployer (Owner): {deployer}")
    print(f"Saldo Deployer: {w3.from_wei(w3.eth.get_balance(deployer), 'ether')} ETH")

    # Deploy contract
    print("Mendeploy PebriCoinShop contract...")
    try:
        PebriCoinShop = w3.eth.contract(abi=abi, bytecode=bytecode)
        
        # Send transaction to deploy
        tx_hash = PebriCoinShop.constructor().transact()
        print("Menunggu konfirmasi transaksi (Wait for Receipt)...")
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        contract_address = tx_receipt.contractAddress
        print(f"Contract berhasil dideploy!")
        print(f"Contract Address: {contract_address}")
        print(f"Transaction Hash: {tx_receipt.transactionHash.hex()}")

        # Save details to config.json
        config = {
            "rpc_url": connected_url,
            "contract_address": contract_address,
            "owner_address": deployer
        }
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)
        print("Konfigurasi deployment berhasil disimpan ke config.json!")
    except Exception as e:
        print(f"Deployment gagal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
