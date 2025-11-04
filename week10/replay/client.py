import socket, time

HOST = "127.0.0.1"
PORT = 50007

def send_login(user="alice"):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    
    token = str(int(time.time()))
    msg = f"LOGIN|{user}|{token}"
    print("[CLIENT] Sending:", msg)
    
    s.sendall(msg.encode())
    
    resp = s.recv(4096)
    print("[CLIENT] Server Response:", resp)
    
    s.close()

if __name__ == "__main__":
    send_login()