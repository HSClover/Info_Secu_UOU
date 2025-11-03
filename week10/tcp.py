from scapy.all import sniff, IP, TCP, conf
from scapy.arch.windows import get_windows_if_list
import threading, socket, time

# 설정
LOOP_TARGET = "127.0.0.1"
PORT = 50007
SNIFF_TIMEOUT = 8
conf.use_pcap = True # pcap 기반 캡처 활성화

# 루프백 인터페이스탐색
def find_loopback_iface():
    for it in get_windows_if_list():
        if 'Loopback' in it.get('name','') or 'Loopback' in it.get('description',''):
            return it.get('name')
    return None

# TCP 플래그 출력
def tcp_flags_str(tcp):
    flags=[]
    if tcp.flags & 0x02: flags.append("SYN")
    if tcp.flags & 0x10: flags.append("ACK")
    if tcp.flags & 0x04: flags.append("RST")
    if tcp.flags & 0x01: flags.append("FIN")
    return "|".join(flags) if flags else "NONE"

# 패킷 수신 시 실행되는 콜백 함수
def packet_printer(pkt):
    if pkt.haslayer(TCP) and pkt.haslayer(IP):
        ip, tcp = pkt[IP], pkt[TCP]
        print(f"[CAPTURE] {ip.src}:{tcp.sport} -> {ip.dst}:{tcp.dport} {tcp_flags_str(tcp)}")
# 스니퍼 실행
def start_sniff(iface, target, port, timeout):
    bpf = f"tcp and host {target} and port {port}"
    print(f"[*] sniffing iface={iface}, filter={bpf}")
    sniff(iface=iface, filter=bpf, prn=packet_printer, timeout=timeout, store=False)

# 서버 코드
def tcp_server():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.bind((LOOP_TARGET, PORT))
    srv.listen(1)
    print(f"[SERVER] listening on {LOOP_TARGET}:{PORT}")
    conn, addr = srv.accept()
    print("[SERVER] connected:", addr)
    data = conn.recv(1024)
    print("[SERVER] recv:", data)
    conn.sendall(b"ACK from server")
    conn.close()
    srv.close()

# 메인 실행
def run_all():
    iface = find_loopback_iface()
    if not iface:
        print("Loopback interface not found. Npcap 설치 확인.")
        return

    # 스니퍼 스레드
    sniffer = threading.Thread(target=start_sniff, args=(iface, LOOP_TARGET, PORT, SNIFF_TIMEOUT), daemon=True)
    sniffer.start()
    time.sleep(0.5)
    # 서버 스레드
    server = threading.Thread(target=tcp_server, daemon=True)
    server.start()
    time.sleep(0.5)

    # 클라이언트
    cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cli.connect((LOOP_TARGET, PORT))
    cli.sendall(b"Hello server")
    resp = cli.recv(1024)
    print("[CLIENT] resp:", resp)
    cli.close()
    sniffer.join()
    print("[*] done")
    
if __name__ == "__main__":
    run_all()