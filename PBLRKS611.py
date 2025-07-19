
import pyfiglet
import os
from deauth_attack import run_deauth_attack
from wpa_cracker import run_wpa_crack
from pico_ducky_handler import run_pico_ducky_attack
from metasploit_handler import run_metasploit_attack

logo = pyfiglet.figlet_format("PBLRKS-611")
print(logo)

def menu():
    while True:
        print("\n===== MENU UTAMA =====")
        print("1. Crack WEP, WPA, WPA2")
        print("2. Packet capture")
        print("3. MiTM attack (WiFi deauth)")
        print("4. Post exploitation Reverse TCP (Metasploit)")
        print("5. Pico Ducky Attack")
        print("6. Keluar")
        choice = input("Masukkan pilihan (1/2/3/4/5): ")

        if choice == '1':
            run_wpa_crack()
        elif choice == '2':
            print("\nPilihan: Packet capture di Raspberry Pi 5 dan decrypt network data\n")
        elif choice == '3':
            run_deauth_attack()
        elif choice == '4':
            run_metasploit_attack()
        elif choice == '5':
            run_pico_ducky_attack()  # <- Memanggil fungsi yang diimpor
        elif choice == '6':
            # print("\nKeluar dari program. Tapi sebelum itu...\n")
            # tampilkan_lirik() 
            print("\nSampai jumpa.\n")
            break
        else:
            print("Pilihan tidak valid. Silakan pilih 1, 2, 3, 4, atau 5.")

if __name__ == "__main__":
    if os.getuid() != 0:
        print("Kesalahan: Skrip ini perlu dijalankan dengan hak akses root.")
        exit()
    menu()
