# server.py
import socket

HOST = "127.0.0.1"
PORT = 50007

def run_server():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(1)
    print("[SERVER] Listening on", HOST, PORT)

    while True:
        conn, addr = srv.accept()
        data = conn.recv(4096)
        
        if not data:
            conn.close()
            continue
            
        msg = data.decode(errors="ignore").strip()
        print(f"[SERVER] Received: {msg}")
    # 단순 처리: 검증 없이 OK 응답
        if msg.startswith("LOGIN|"):
            conn.sendall(b"OK")
        else:
            conn.sendall(b"ERR")

        conn.close()

if __name__ == "__main__":
    run_server()