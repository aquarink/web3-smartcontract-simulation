import os
import json
import hashlib
import time
from web3 import Web3
from eth_account import Account

# ANSI Escape Colors for Beautiful Terminal Output
GREEN = "\033[92m"
BLUE = "\033[94m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
RESET = "\033[0m"

def print_header(title):
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{CYAN}🔹 {title.upper()} 🔹{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")

def get_web3_and_contract():
    if not os.path.exists("config.json") or not os.path.exists("contract_data.json"):
        return None, None, None
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        with open("contract_data.json", "r") as f:
            contract_data = json.load(f)
        
        w3 = Web3(Web3.HTTPProvider(config["rpc_url"]))
        contract = w3.eth.contract(address=config["contract_address"], abi=contract_data["abi"])
        return w3, contract, config
    except Exception as e:
        print(f"Error loading configs: {e}")
        return None, None, None

def sha256_hash(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def main():
    w3, contract, config = get_web3_and_contract()
    if not w3 or not w3.is_connected():
        print(f"{RED}{BOLD}ERROR: Gagal terhubung ke Ethereum Node.{RESET}")
        print(f"Pastikan Ganache/Anvil Anda sudah berjalan, lalu jalankan:")
        print(f"  {YELLOW}python3 deploy.py{RESET} untuk mendeploy contract terlebih dahulu!")
        return

    # Connection Header
    print_header("Inisialisasi Blockchain Node")
    print(f"🌐 Node URL         : {GREEN}{config['rpc_url']}{RESET}")
    print(f"📜 Contract Address : {GREEN}{config['contract_address']}{RESET}")
    print(f"🏢 Owner Address    : {GREEN}{config['owner_address']}{RESET}")
    print(f"📦 Blok Terbaru     : {GREEN}#{w3.eth.block_number}{RESET}")

    # Step 1: Cryptography Hashing Demonstration
    print_header("Langkah 1: Simulasi Hashing Kredensial (Client-Side)")
    print("Mendaftarkan Pengguna Baru secara lokal...")
    email = input(f"{BOLD}Masukkan Email Pengguna Baru: {RESET}").strip()
    password = input(f"{BOLD}Masukkan Password Pengguna Baru: {RESET}").strip()

    pwd_hash = sha256_hash(password)
    print(f"\n🔄 {BOLD}Meng-hash Password dengan Kriptografi SHA-256:{RESET}")
    print(f"  🔑 Raw Password   : {YELLOW}{password}{RESET}")
    print(f"  🔐 Hashed Result   : {GREEN}{pwd_hash}{RESET}")
    print(f"\n💡 {BLUE}Edukasi Kuliah:{RESET}")
    print("   Database server hanya akan menyimpan string hash di atas. Jika user melakukan login,")
    print("   password masukan di-hash ulang dan dicocokkan dengan hash database. Password asli")
    print("   tidak pernah berpindah atau disimpan di blockchain!")

    time.sleep(2.0)

    # Step 2: Keypair Wallet Generation
    print_header("Langkah 2: Pembuatan Kunci Dompet Kripto (Wallet Keypair)")
    print("Meng-generate Pasangan Kunci Kriptografis Baru (Address & Private Key)...")
    new_account = Account.create()
    user_address = new_account.address
    user_private_key = new_account.key.hex()
    
    time.sleep(1.0)
    print(f"  📬 Address Publik  : {CYAN}{user_address}{RESET}")
    print(f"  🔑 Private Key     : {RED}{user_private_key}{RESET}")
    print(f"\n💡 {BLUE}Edukasi Kuliah:{RESET}")
    print(f"   • {UNDERLINE}Address Publik{RESET} bertindak seperti nomor rekening bank untuk menerima dana.")
    print(f"   • {UNDERLINE}Private Key{RESET} bertindak seperti tanda tangan digital rahasia untuk menyetujui transaksi.")

    time.sleep(2.0)

    # Step 3: Registration Blockchain Faucet (ETH & Coins)
    print_header("Langkah 3: Registrasi Faucet (Pengiriman ETH & Minting Coin)")
    owner_address = config["owner_address"]
    
    print(f"Mengirim {YELLOW}1.0 ETH Gas Fee{RESET} dari dompet Owner ({owner_address[:8]}...) ke dompet baru Anda...")
    try:
        tx_hash_eth = w3.eth.send_transaction({
            'from': owner_address,
            'to': user_address,
            'value': w3.to_wei(1, 'ether')
        })
        print(f"⏳ Menunggu konfirmasi transaksi Gas Fee...")
        w3.eth.wait_for_transaction_receipt(tx_hash_eth)
        print(f"  ✅ {GREEN}Gas Fee Terkirim!{RESET} Tx Hash: {GREEN}{tx_hash_eth.hex()}{RESET}")
    except Exception as e:
        print(f"{RED}Gagal mentransfer ETH: {e}{RESET}")
        return

    time.sleep(1.5)

    print(f"\nMencetak (Minting) {YELLOW}100 Pebri Coin (PEBRI){RESET} ke Dompet baru Anda melalui Smart Contract...")
    try:
        tx_hash_mint = contract.functions.mint(user_address, 100).transact({'from': owner_address})
        print(f"⏳ Menunggu konfirmasi transaksi Minting...")
        w3.eth.wait_for_transaction_receipt(tx_hash_mint)
        print(f"  ✅ {GREEN}Koin Berhasil Dicetak!{RESET} Tx Hash: {GREEN}{tx_hash_mint.hex()}{RESET}")
    except Exception as e:
        print(f"{RED}Gagal mencetak Pebri Coin: {e}{RESET}")
        return

    time.sleep(2.0)

    # Step 4: Loading state before shopping
    user_coin_bal = contract.functions.balanceOf(user_address).call()
    user_eth_bal = w3.from_wei(w3.eth.get_balance(user_address), 'ether')
    owner_coin_bal = contract.functions.balanceOf(owner_address).call()
    owner_eth_bal = w3.from_wei(w3.eth.get_balance(owner_address), 'ether')
    product_name = contract.functions.productName().call()
    product_price = contract.functions.productPrice().call()
    product_stock = contract.functions.productStock().call()

    print_header("Langkah 4: Status Saldo Pengguna & Smart Contract")
    print(f"{BOLD}Saldo Pengguna Baru:{RESET}")
    print(f"  • Pebri Coin  : {GREEN}{user_coin_bal} PEBRI{RESET}")
    print(f"  • Gas Fee ETH : {GREEN}{user_eth_bal} ETH{RESET}")
    
    print(f"\n{BOLD}Saldo Pemilik Aplikasi (Owner):{RESET}")
    print(f"  • Pebri Coin  : {GREEN}{owner_coin_bal} PEBRI{RESET}")
    print(f"  • Gas Fee ETH : {GREEN}{owner_eth_bal} ETH{RESET}")
    
    print(f"\n{BOLD}Data Buku di Smart Contract:{RESET}")
    print(f"  • Buku        : {CYAN}{product_name}{RESET}")
    print(f"  • Harga       : {YELLOW}{product_price} PEBRI / Pcs{RESET}")
    print(f"  • Stok        : {YELLOW}{product_stock} Pcs{RESET}")

    time.sleep(2.0)

    # Step 5: Simulation of purchase (Signed transaction)
    print_header("Langkah 5: Pembelian Buku (Client-Side Signed Transaction)")
    print(f"Membeli Buku '{product_name}'...")
    try:
        qty = int(input(f"{BOLD}Masukkan jumlah buku yang dibeli: {RESET}"))
    except ValueError:
        qty = 1

    total_cost = qty * product_price
    print(f"\nMenghitung total pembayaran: {qty} x {product_price} PEBRI = {YELLOW}{total_cost} PEBRI{RESET}")

    if product_stock < qty:
        print(f"{RED}Transaksi Dibatalkan: Stok produk tidak mencukupi!{RESET}")
        return
    if user_coin_bal < total_cost:
        print(f"{RED}Transaksi Dibatalkan: Saldo Pebri Coin Anda kurang!{RESET}")
        return

    time.sleep(1.0)

    print(f"\n🛠️  {BOLD}Sub-langkah A: Membangun Payload Transaksi (beliBarang)...{RESET}")
    nonce = w3.eth.get_transaction_count(user_address)
    tx = contract.functions.beliBarang(qty).build_transaction({
        'from': user_address,
        'nonce': nonce,
        'gas': 250000,
        'gasPrice': w3.eth.gas_price
    })
    print(f"  📝 Payload JSON: {BLUE}{json.dumps({k: str(v) for k, v in tx.items()})}{RESET}")

    time.sleep(1.5)

    print(f"\n✍️  {BOLD}Sub-langkah B: Menandatangani Transaksi dengan Private Key Pengguna...{RESET}")
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=user_private_key)
    print(f"  🔑 Signature Hash: {GREEN}{signed_tx.hash.hex()}{RESET}")
    print("  (Proses tanda tangan terjadi offline di lokal klien, rahasia private key tidak bocor!)")

    time.sleep(1.5)

    print(f"\n🚀 {BOLD}Sub-langkah C: Memancarkan (Broadcast) Transaksi ke Ethereum Node...{RESET}")
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print("  Mengirim raw transaksi ke blockchain network...")
    
    time.sleep(1.0)
    print("⏳ Menunggu konfirmasi penambang blok (Mining Block)...")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    print(f"\n✅ {GREEN}{BOLD}TRANSAKSI BERHASIL MASUK BLOK #{receipt.blockNumber}!{RESET}")
    print(f"  • Transaction Hash : {GREEN}{receipt.transactionHash.hex()}{RESET}")
    print(f"  • Gas yang Digunakan: {CYAN}{receipt.gasUsed} gas units{RESET}")

    time.sleep(2.0)

    # Step 6: Final balances check
    user_coin_bal_new = contract.functions.balanceOf(user_address).call()
    user_eth_bal_new = w3.from_wei(w3.eth.get_balance(user_address), 'ether')
    owner_coin_bal_new = contract.functions.balanceOf(owner_address).call()
    owner_eth_bal_new = w3.from_wei(w3.eth.get_balance(owner_address), 'ether')
    product_stock_new = contract.functions.productStock().call()

    print_header("Langkah 6: Status Saldo Akhir Setelah Transaksi")
    print(f"{BOLD}Saldo Pengguna Baru:{RESET}")
    print(f"  • Pebri Coin  : {GREEN}{user_coin_bal_new} PEBRI{RESET} (Berkurang {total_cost} PEBRI)")
    print(f"  • Gas Fee ETH : {GREEN}{user_eth_bal_new} ETH{RESET} (Berkurang untuk biaya transaksi)")
    
    print(f"\n{BOLD}Saldo Pemilik Aplikasi (Owner):{RESET}")
    print(f"  • Pebri Coin  : {GREEN}{owner_coin_bal_new} PEBRI{RESET} (Bertambah +{total_cost} PEBRI)")
    print(f"  • Gas Fee ETH : {GREEN}{owner_eth_bal_new} ETH{RESET}")
    
    print(f"\n{BOLD}Stok Buku Smart Contract Terupdate:{RESET}")
    print(f"  • Stok Terbaru: {YELLOW}{product_stock_new} Pcs{RESET} (Berkurang {qty} Pcs)")

    print(f"\n{BOLD}{GREEN}🌟 === SIMULASI CLI BERHASIL DISELESAIKAN === 🌟{RESET}\n")

if __name__ == "__main__":
    main()
