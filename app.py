import streamlit as st
import json
import os
import hashlib
import time
from web3 import Web3
from eth_account import Account

# Page Configuration
st.set_page_config(
    page_title="Web3 Jual-Beli Pebri Coin Simulation",
    page_icon="🪙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium UI & Aesthetics
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Space+Grotesk:wght@400;500;700&display=swap');
    
    /* Overall Theme Overrides */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0d0f1a 0%, #171b30 50%, #0d0f1a 100%);
        color: #e2e8f0;
    }
    
    /* Header Customization */
    h1, h2, h3, h4 {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    .main-title {
        background: linear-gradient(45deg, #6366f1, #a855f7, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 5px;
    }
    
    .subtitle {
        text-align: center;
        color: #94a3b8;
        font-size: 1.15rem;
        margin-bottom: 30px;
    }

    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(30, 41, 59, 0.45);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }
    
    .glass-card-header {
        font-size: 1.25rem;
        font-weight: 600;
        color: #f1f5f9;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 10px;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* Input Fields Styling */
    div[data-baseweb="input"] {
        background-color: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
    }
    
    /* Metrics Customization */
    div[data-testid="stMetricValue"] {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(45deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Status Boxes */
    .status-box {
        padding: 12px 16px;
        border-radius: 8px;
        font-size: 0.95rem;
        margin-bottom: 15px;
        border-left: 4px solid;
    }
    
    .status-success {
        background: rgba(16, 185, 129, 0.15);
        border-left-color: #10b981;
        color: #34d399;
    }
    
    .status-info {
        background: rgba(59, 130, 246, 0.15);
        border-left-color: #3b82f6;
        color: #60a5fa;
    }
    
    .status-warning {
        background: rgba(245, 158, 11, 0.15);
        border-left-color: #f59e0b;
        color: #fbbf24;
    }

    /* Real-Time Hash Stream Visualizer */
    .hash-container {
        background-color: #020617;
        border: 1px solid #1e293b;
        font-family: 'Courier New', Courier, monospace;
        padding: 12px;
        border-radius: 8px;
        color: #38bdf8;
        overflow-x: auto;
        white-space: pre-wrap;
        word-break: break-all;
        font-size: 0.9rem;
    }
    
    .hash-label {
        font-size: 0.8rem;
        color: #94a3b8;
        margin-bottom: 4px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Flowchart Animation & Middleman CSS Diagram */
    .flow-wrapper {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        padding: 20px 10px;
        gap: 15px;
    }
    
    .flow-node {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        flex: 1;
        min-width: 140px;
        position: relative;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    
    .flow-node.active {
        border-color: #a855f7;
        box-shadow: 0 0 15px rgba(168, 85, 247, 0.4);
    }
    
    .flow-node h5 {
        margin: 0 0 5px 0;
        color: #f8fafc;
        font-size: 0.95rem;
    }
    
    .flow-node p {
        margin: 0;
        font-size: 0.8rem;
        color: #94a3b8;
    }
    
    .flow-arrow {
        color: #6366f1;
        font-weight: bold;
        font-size: 1.5rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        animation: pulse 1.5s infinite;
    }
    
    .flow-arrow-text {
        font-size: 0.7rem;
        color: #a855f7;
        text-transform: uppercase;
        margin-top: -5px;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 0.4; transform: scale(1); }
        50% { opacity: 1; transform: scale(1.1); }
    }
    
    /* Custom transaction animation */
    .tx-animation-box {
        background: #090d16;
        border: 1px dashed rgba(168, 85, 247, 0.4);
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin-top: 15px;
    }
    
    .coin-flow {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 30px;
        margin: 20px 0;
    }
    
    .coin {
        font-size: 2rem;
        animation: spin-and-fly 2s infinite linear;
    }
    
    @keyframes spin-and-fly {
        0% { transform: rotate(0deg) translateX(-40px); opacity: 0; }
        10% { opacity: 1; }
        90% { opacity: 1; }
        100% { transform: rotate(360deg) translateX(40px); opacity: 0; }
    }
</style>
""", unsafe_allow_html=True)

# File DB Configurations
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

# Web3 Helpers
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

# Initialization of web3
w3, contract, config = get_web3_and_contract()

# Session State Initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""
if 'user_address' not in st.session_state:
    st.session_state.user_address = ""
if 'user_private_key' not in st.session_state:
    st.session_state.user_private_key = ""

# Sidebar - Node Connection Status
with st.sidebar:
    st.markdown('<div style="text-align: center;"><span style="font-size: 3rem;">🪙</span></div>', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #fff;'>Blockchain Node</h3>", unsafe_allow_html=True)
    
    if w3:
        st.markdown(f"""
        <div class="status-box status-success">
            <b>Status: Connected ✅</b><br>
            Network: Local Simulation (Ganache/Anvil)<br>
            Node URL: <code>{config['rpc_url']}</code><br>
            Contract: <code>{config['contract_address'][:8]}...{config['contract_address'][-6:]}</code>
        </div>
        """, unsafe_allow_html=True)
        
        # Display block info
        latest_block = w3.eth.block_number
        st.metric(label="Latest Block Number", value=latest_block)
    else:
        st.markdown("""
        <div class="status-box status-warning">
            <b>Status: Disconnected ❌</b><br>
            Local simulator node tidak terdeteksi.<br>
            Silakan baca panduan Setup di halaman utama.
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    
    # Lecture Guide section
    st.markdown("<h4 style='color: #a855f7;'>Panduan Edukasi Kuliah</h4>", unsafe_allow_html=True)
    st.markdown("""
    Aplikasi ini dirancang untuk menunjukkan:
    1. **Client-Side Hashing**: Bagaimana password diubah menjadi hash unik sebelum dikirim ke database.
    2. **Fungsi Blockchain Faucet**: Pendistribusian modal koin & Gas Fee (ETH) pada saat pendaftaran pengguna baru.
    3. **Smart Contract sebagai Middleman**: Smart contract memverifikasi saldo, mengubah kepemilikan koin, dan mengurangi stok barang secara otonom tanpa perantara database tradisional.
    4. **Client-side Signing**: Transaksi belanja ditandatangani lokal oleh private key pembeli, lalu dikirim ke Blockchain.
    """)

# Main Title Area
st.markdown('<div class="main-title">Pebri Coin Shop</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Simulasi Jual-Beli & Kriptografi untuk Edukasi Smart Contract</div>', unsafe_allow_html=True)

# Error Screen if Web3 Connection Fails
if not w3:
    st.markdown("""
    <div class="glass-card">
        <div class="glass-card-header">🛠️ Panduan Konfigurasi & Setup Simulasi</div>
        <p>Aplikasi belum mendeteksi deployment Smart Contract atau Local Node (Ganache / Anvil).</p>
        <p>Silakan ikuti langkah-langkah di bawah untuk memulai simulasi:</p>
        <ol>
            <li>
                <b>Jalankan Blockchain Node Lokal:</b>
                <pre><code>anvil</code></pre>
                atau menggunakan Ganache CLI:
                <pre><code>npx ganache-cli</code></pre>
            </li>
            <li>
                <b>Kompilasi Smart Contract:</b>
                <pre><code>python compile_contract.py</code></pre>
                <i>(Ini akan mengunduh compiler Solidity 0.8.20 dan menghasilkan ABI/Bytecode di <code>contract_data.json</code>)</i>
            </li>
            <li>
                <b>Deploy Contract ke Node Lokal:</b>
                <pre><code>python deploy.py</code></pre>
                <i>(Ini akan mendeteksi node yang aktif, mendeploy contract, dan membuat file konfigurasi <code>config.json</code>)</i>
            </li>
            <li>
                <b>Jalankan Streamlit App:</b>
                <pre><code>streamlit run app.py</code></pre>
            </li>
        </ol>
        <div class="status-box status-info">
            <b>Kenapa Menggunakan Simulator Lokal?</b><br>
            Simulator seperti Ganache/Anvil memproses transaksi secara instan (&lt;1 detik). Ini sangat ideal untuk demonstrasi kelas agar mahasiswa dapat melihat perubahan saldo langsung di layar tanpa harus menunggu block confirmation Testnet publik (Sepolia) yang memakan waktu 12-15 detik.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Helper hash function for visual display
def sha256_visual(password):
    if not password:
        return "", ""
    hash_obj = hashlib.sha256(password.encode('utf-8'))
    hex_digest = hash_obj.hexdigest()
    # Convert hex digest to a binary bitstream string representation for visualization
    bin_digest = "".join(f"{int(c, 16):04b} " for c in hex_digest[:16]) + "..."
    return hex_digest, bin_digest

# App Logic Routing
if not st.session_state.logged_in:
    # ------------------ AUTHENTICATION PAGE ------------------
    tab1, tab2 = st.tabs(["🔑 Login Pengguna", "📝 Register Pengguna Baru"])
    
    with tab1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="glass-card-header">🔑 Masuk ke Aplikasi</div>', unsafe_allow_html=True)
        
        login_email = st.text_input("Email", placeholder="contoh@mahasiswa.ac.id", key="login_email_input")
        login_password = st.text_input("Password", type="password", key="login_pass_input")
        
        # Real-time SHA-256 visualization for input password
        if login_password:
            hex_hash, bin_hash = sha256_visual(login_password)
            st.markdown(f"""
            <div style="margin-top: 10px;">
                <div class="hash-label">Visualisasi Kriptografi: Client-Side SHA-256 Hash</div>
                <div class="hash-container">
<b>Plain Password:</b> {login_password}<br>
<b>SHA-256 Hex:</b> {hex_hash}<br>
<b>Bit Stream (16 karakter pertama):</b> {bin_hash}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        login_btn = st.button("Masuk Sekarang 🚀", type="primary", use_container_width=True)
        
        if login_btn:
            if not login_email or not login_password:
                st.error("Silakan isi email dan password!")
            else:
                users = load_users()
                hashed_input, _ = sha256_visual(login_password)
                
                if login_email in users:
                    user_data = users[login_email]
                    if user_data["password_hash"] == hashed_input:
                        st.session_state.logged_in = True
                        st.session_state.user_email = login_email
                        st.session_state.user_address = user_data["address"]
                        st.session_state.user_private_key = user_data["private_key"]
                        st.success("Login berhasil!")
                        st.rerun()
                    else:
                        st.error("Password salah!")
                else:
                    st.error("Email belum terdaftar!")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with tab2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="glass-card-header">📝 Registrasi & Pembuatan Akun Blockchain</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            reg_email = st.text_input("Email Baru", placeholder="mahasiswa@univ.ac.id")
            reg_password = st.text_input("Password Baru", type="password")
            reg_repassword = st.text_input("Ulangi Password", type="password")
            
        with col2:
            st.markdown("""
            ##### Edukasi Kriptografi Registrasi:
            Saat Anda menekan 'Register':
            1. Password Anda akan di-hash secara lokal di browser.
            2. Sebuah **Ethereum Wallet (Address & Private Key)** unik akan di-generate secara lokal.
            3. Server akan mendeteksi akun baru tersebut dan mengirimkan modal awal dari Smart Contract.
            """)
            
            # Show live hashing comparison as user types
            if reg_password:
                hex_hash, bin_hash = sha256_visual(reg_password)
                st.markdown(f"""
                <div class="hash-label">Visualisasi Hash Password Pendaftaran</div>
                <div class="hash-container">
<b>Raw:</b> {reg_password}<br>
<b>SHA-256:</b> {hex_hash}
                </div>
                """, unsafe_allow_html=True)
                
                if reg_repassword and reg_password != reg_repassword:
                    st.markdown("<p style='color:#ef4444; font-size:0.9rem;'>⚠️ Password tidak cocok!</p>", unsafe_allow_html=True)
                elif reg_repassword and reg_password == reg_repassword:
                    st.markdown("<p style='color:#10b981; font-size:0.9rem;'>✅ Password cocok!</p>", unsafe_allow_html=True)

        reg_btn = st.button("Daftar & Minta Modal Simulasi 🪙", type="secondary", use_container_width=True)
        
        if reg_btn:
            if not reg_email or not reg_password or not reg_repassword:
                st.error("Harap isi semua input!")
            elif reg_password != reg_repassword:
                st.error("Ulangi password dengan benar!")
            else:
                users = load_users()
                if reg_email in users:
                    st.error("Email sudah terdaftar!")
                else:
                    # Proceed with account creation
                    with st.status("Memproses Pembuatan Akun Blockchain...", expanded=True) as status:
                        # 1. Cryptographic hash
                        status.write("🔑 1. Meng-hash password menggunakan SHA-256...")
                        hashed_pass, _ = sha256_visual(reg_password)
                        time.sleep(0.6) # Edu simulation delay
                        
                        # 2. Generating Ethereum Account
                        status.write("🌐 2. Meng-generate pasangan kunci kriptografi (Address & Private Key) baru...")
                        new_account = Account.create()
                        user_address = new_account.address
                        user_private_key = new_account.key.hex()
                        time.sleep(0.6)
                        
                        # 3. Fund ETH from Owner for Gas Fee
                        owner_address = config["owner_address"]
                        status.write(f"⛽ 3. Mentransfer 1 ETH Gas Fee dari owner ({owner_address[:8]}...) ke address Anda ({user_address[:8]}...)...")
                        
                        try:
                            # Transfer 1 ETH
                            tx_hash_eth = w3.eth.send_transaction({
                                'from': owner_address,
                                'to': user_address,
                                'value': w3.to_wei(1, 'ether')
                            })
                            status.write(f"✔️ Gas fee berhasil ditransfer! Tx Hash: {tx_hash_eth.hex()[:15]}...")
                            w3.eth.wait_for_transaction_receipt(tx_hash_eth)
                            time.sleep(0.6)
                        except Exception as e:
                            status.update(label="Registrasi Gagal!", state="error")
                            st.error(f"Gagal mengirim Gas Fee: {e}")
                            st.stop()
                        
                        # 4. Mint 100 Pebri Coins (ERC20-like transfer)
                        status.write(f"🪙 4. Mencetak 100 Pebri Coin ke address baru Anda...")
                        try:
                            tx_hash_mint = contract.functions.mint(user_address, 100).transact({'from': owner_address})
                            status.write(f"✔️ Pebri Coin dicetak! Tx Hash: {tx_hash_mint.hex()[:15]}...")
                            w3.eth.wait_for_transaction_receipt(tx_hash_mint)
                            time.sleep(0.6)
                        except Exception as e:
                            status.update(label="Registrasi Gagal!", state="error")
                            st.error(f"Gagal mencetak Pebri Coin: {e}")
                            st.stop()
                            
                        # Save details in json db
                        users[reg_email] = {
                            "password_hash": hashed_pass,
                            "address": user_address,
                            "private_key": user_private_key,
                            "created_at": time.time()
                        }
                        save_users(users)
                        
                        status.update(label="Akun Berhasil Dibuat!", state="complete")
                        
                    st.success(f"Akun berhasil didaftarkan! Address Anda: {user_address}")
                    st.info("Sekarang Anda dapat login menggunakan tab Login Pengguna.")
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # ------------------ DASHBOARD PAGE ------------------
    # Header dashboard
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(30, 41, 59, 0.3); padding: 12px 24px; border-radius: 12px; margin-bottom: 25px; border: 1px solid rgba(255, 255, 255, 0.05);">
        <div>
            <span style="color: #94a3b8; font-size: 0.9rem;">LOGGED IN AS</span><br>
            <strong style="color: #fff; font-size: 1.1rem;">{st.session_state.user_email}</strong>
        </div>
        <div>
            <span style="color: #94a3b8; font-size: 0.9rem;">WALLET ADDRESS</span><br>
            <code style="background: #0f172a; color: #38bdf8; padding: 4px 8px; border-radius: 6px; font-size: 0.9rem;">{st.session_state.user_address}</code>
        </div>
        <div>
            <button onclick="window.location.reload();" style="background: #3b82f6; color: white; border: none; padding: 8px 16px; border-radius: 8px; font-weight: 600; cursor: pointer;" 
            id="btn_logout">Logout Session</button>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Capture Streamlit button event to handle logout properly
    col_out1, col_out2, col_out3 = st.columns([1,1,6])
    with col_out1:
        if st.button("Keluar Akun 🚪", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_email = ""
            st.session_state.user_address = ""
            st.session_state.user_private_key = ""
            st.rerun()

    # Load Smart Contract data
    owner_address = config["owner_address"]
    product_name = contract.functions.productName().call()
    product_price = contract.functions.productPrice().call()
    product_stock = contract.functions.productStock().call()
    
    # Load balances
    try:
        user_coin_bal = contract.functions.balanceOf(st.session_state.user_address).call()
        user_eth_bal = w3.from_wei(w3.eth.get_balance(st.session_state.user_address), 'ether')
        
        owner_coin_bal = contract.functions.balanceOf(owner_address).call()
        owner_eth_bal = w3.from_wei(w3.eth.get_balance(owner_address), 'ether')
    except Exception as e:
        st.error(f"Gagal membaca data dari Smart Contract: {e}")
        st.stop()
        
    # Layout Grid: 2 columns
    left_col, right_col = st.columns([2, 3])
    
    with left_col:
        # A. Visualisasi Hash Credential Login
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="glass-card-header">🔑 A. Kredensial & Validasi Hash Kriptografi</div>', unsafe_allow_html=True)
        
        users = load_users()
        saved_hash = users[st.session_state.user_email]["password_hash"]
        
        st.markdown(f"""
        <p>Dalam database simulasi <code>users.json</code>, kami <b>tidak</b> menyimpan password teks asli Anda. Kami hanya mencocokkan hash SHA-256 yang dibuat di sisi browser:</p>
        <div class="hash-label">Saved Hash in Database (users.json)</div>
        <div class="hash-container" style="color: #a855f7;">
{saved_hash}
        </div>
        <p style="margin-top: 10px; font-size: 0.85rem; color: #94a3b8;">
            💡 <i>Setiap kali Anda login, password masukan di-hash ulang dan dicocokkan dengan nilai di atas. Jika satu huruf saja berbeda, nilai hash akan berubah total (Efek Avalanche).</i>
        </p>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Real-time Balances Cards
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="glass-card-header">💰 Saldo Real-Time Blockchain</div>', unsafe_allow_html=True)
        
        bal_col1, bal_col2 = st.columns(2)
        with bal_col1:
            st.metric("Saldo Pebri Coin Anda", f"{user_coin_bal} PEBRI")
            st.markdown(f"<span style='font-size: 0.85rem; color:#94a3b8;'>Gas Fee: {user_eth_bal:.4f} ETH</span>", unsafe_allow_html=True)
        with bal_col2:
            st.metric("Saldo Pemilik Aplikasi", f"{owner_coin_bal} PEBRI")
            st.markdown(f"<span style='font-size: 0.85rem; color:#94a3b8;'>Gas Fee: {owner_eth_bal:.4f} ETH</span>", unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)

    with right_col:
        # B. Diagram Arsitektur Middleman Smart Contract
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="glass-card-header">🔗 B. Posisi Smart Contract sebagai Middleman</div>', unsafe_allow_html=True)
        
        # Beautiful CSS based flow representation
        st.markdown(f"""
        <div class="flow-wrapper">
            <div class="flow-node">
                <h5>1. User Browser</h5>
                <p>Streamlit App / Local Key</p>
                <code style="font-size: 0.7rem; color: #38bdf8;">{st.session_state.user_address[:6]}...</code>
            </div>
            <div class="flow-arrow">
                ➡️
                <span class="flow-arrow-text">Sign Tx</span>
            </div>
            <div class="flow-node active">
                <h5>2. Smart Contract</h5>
                <p>PebriCoinShop.sol</p>
                <code style="font-size: 0.7rem; color: #a855f7;">{config['contract_address'][:6]}...</code>
            </div>
            <div class="flow-arrow">
                ➡️
                <span class="flow-arrow-text">Verify & Execute</span>
            </div>
            <div class="flow-node">
                <h5>3. Owner Address</h5>
                <p>Dompet Pemilik</p>
                <code style="font-size: 0.7rem; color: #34d399;">{owner_address[:6]}...</code>
            </div>
        </div>
        <p style="font-size: 0.85rem; color: #94a3b8; text-align: center; margin-top: 10px;">
            <i>Aplikasi Web tidak memegang kontrol atas koin. Kontrak <code>PebriCoinShop</code> bertindak sebagai perantara otomatis yang mengawasi aturan belanja barang.</i>
        </p>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # C. Transaksi Toko & Animasi Aliran Dana
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="glass-card-header">🛒 C. Transaksi Pembelian Barang</div>', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background: rgba(99, 102, 241, 0.1); padding: 15px; border-radius: 10px; margin-bottom: 20px; border: 1px solid rgba(99, 102, 241, 0.2);">
            <h4 style="margin: 0; color: #fff;">📘 {product_name}</h4>
            <div style="display: flex; justify-content: space-between; margin-top: 10px; font-size: 0.95rem;">
                <span>Harga per Buku: <b>{product_price} PEBRI</b></span>
                <span>Stok Saat Ini: <b style="color: #38bdf8;">{product_stock} Pcs</b></span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # User input quantity
        quantity = st.number_input("Jumlah Buku yang Ingin Dibeli", min_value=1, max_value=int(product_stock) if product_stock > 0 else 1, value=1, step=1)
        total_cost = quantity * product_price
        
        st.markdown(f"**Total Pembayaran:** `{total_cost} Pebri Coin`")
        
        # Validation checks before buying
        can_buy = True
        if product_stock == 0:
            st.error("Maaf, stok barang habis!")
            can_buy = False
        elif user_coin_bal < total_cost:
            st.error("Saldo Pebri Coin Anda tidak mencukupi untuk transaksi ini.")
            can_buy = False
            
        buy_btn = st.button("Beli Buku Sekarang (Kirim Transaksi Blockchain) 💳", type="primary", disabled=not can_buy, use_container_width=True)
        
        if buy_btn:
            # We will use st.status to show step-by-step signed simulation
            with st.status("Memulai Transaksi Blockchain Jual-Beli...", expanded=True) as tx_status:
                tx_status.write("🛠️ 1. Membangun Payload Transaksi (Calling `beliBarang` function in Smart Contract)...")
                time.sleep(0.8) # Simulating step-by-step execution for lecture clarity
                
                # Build transaction dict
                try:
                    nonce = w3.eth.get_transaction_count(st.session_state.user_address)
                    gas_estimate = contract.functions.beliBarang(quantity).estimate_hash = 200000 # default fallback or estimate
                    
                    tx = contract.functions.beliBarang(quantity).build_transaction({
                        'from': st.session_state.user_address,
                        'nonce': nonce,
                        'gas': 250000,
                        'gasPrice': w3.eth.gas_price
                    })
                    tx_status.write("Payload berhasil dibangun.")
                except Exception as e:
                    tx_status.update(label="Transaksi Gagal!", state="error")
                    st.error(f"Gagal membangun transaksi: {e}")
                    st.stop()
                    
                tx_status.write("✍️ 2. Menandatangani Transaksi Lokal di Sisi Klien menggunakan Private Key Anda...")
                time.sleep(0.8)
                
                try:
                    signed_tx = w3.eth.account.sign_transaction(tx, private_key=st.session_state.user_private_key)
                    tx_status.write("Transaksi berhasil ditandatangani secara kriptografis.")
                except Exception as e:
                    tx_status.update(label="Transaksi Gagal!", state="error")
                    st.error(f"Gagal menandatangani transaksi: {e}")
                    st.stop()
                
                # Animasi Aliran Saldo (Custom HTML Animation)
                tx_status.write("🚀 3. Memancarkan (Broadcasting) Transaksi ke Ethereum Node Lokal...")
                st.markdown(f"""
                <div class="tx-animation-box">
                    <p style="margin: 0; font-size: 0.85rem; color: #a855f7; font-weight: bold; text-transform: uppercase;">Simulasi Transaksi Sedang Berjalan</p>
                    <div class="coin-flow">
                        <span>👦 Dompet User ({user_coin_bal} Pebri)</span>
                        <span class="coin">🪙</span>
                        <span>📜 Smart Contract</span>
                        <span class="coin">🪙</span>
                        <span>🏢 Pemilik ({owner_coin_bal} Pebri)</span>
                    </div>
                    <p style="margin: 0; color: #94a3b8; font-size: 0.8rem;">Mengirim {total_cost} Pebri Coin & Memotong Stok Buku sebanyak {quantity} Pcs...</p>
                </div>
                """, unsafe_allow_html=True)
                time.sleep(1.2)
                
                try:
                    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                    tx_status.write(f"Tx Hash Terbit: `{tx_hash.hex()}`. Menunggu Konfirmasi Blok (Receipt)...")
                except Exception as e:
                    tx_status.update(label="Transaksi Gagal!", state="error")
                    st.error(f"Gagal mengirim transaksi: {e}")
                    st.stop()
                    
                # Mining Receipt
                try:
                    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                    tx_status.write(f"✔️ Transaksi Berhasil Masuk Blok #{tx_receipt.blockNumber}!")
                    tx_status.write(f"Gas yang Digunakan: `{tx_receipt.gasUsed}` gwei")
                    time.sleep(0.8)
                except Exception as e:
                    tx_status.update(label="Transaksi Gagal!", state="error")
                    st.error(f"Gagal konfirmasi block: {e}")
                    st.stop()
                    
                tx_status.update(label="Pembelian Buku Sukses! 🎉", state="complete")
                st.balloons()
                
            # Show receipt box
            st.markdown(f"""
            <div class="status-box status-success" style="margin-top: 15px;">
                <b>Detail Transaksi Berhasil:</b><br>
                • Transaksi Hash: <code>{tx_receipt.transactionHash.hex()}</code><br>
                • Block Number: <code>{tx_receipt.blockNumber}</code><br>
                • Gas Digunakan: <code>{tx_receipt.gasUsed} gas units</code><br>
                • Pengirim: <code>{tx_receipt['from']}</code><br>
                • Status: <code>Success (1)</code>
            </div>
            """, unsafe_allow_html=True)
            
            # Use interactive button to refresh
            st.button("Perbarui Saldo / Refresh Dashboard 🔄", type="secondary")
            
        st.markdown('</div>', unsafe_allow_html=True)
        
        # D. Bagian Refill Stock untuk Owner / Demonstran
        if st.session_state.user_address == owner_address:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<div class="glass-card-header">⚙️ Panel Demonstrator (Owner Only)</div>', unsafe_allow_html=True)
            
            refill_amount = st.number_input("Jumlah Refill Stok Buku", min_value=1, max_value=500, value=50)
            refill_btn = st.button("Lakukan Refill Stok 🔄", type="secondary")
            
            if refill_btn:
                try:
                    # Run transaction from unlocked owner node account
                    tx_hash = contract.functions.refillStock(refill_amount).transact({'from': owner_address})
                    w3.eth.wait_for_transaction_receipt(tx_hash)
                    st.success(f"Stok berhasil di-refill sebanyak {refill_amount}! Dashboard terupdate.")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal me-refill stok: {e}")
            st.markdown('</div>', unsafe_allow_html=True)
