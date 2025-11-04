# packet_replay_lab.py
# 로컬(127.0.0.1) 패킷 캡처 & 재연(드라이런 기본)
from scapy.all import sniff, TCP, IP, Raw, conf
from scapy.arch.windows import get_windows_if_list
import socket, time

conf.use_pcap = True
HOST = "127.0.0.1"
PORT = 50007
EXECUTE = False         # 실제 재전송하려면 True
SNIFF_TIMEOUT = 15      # 캡처 대기 시간(초) 넉넉히
AUTO_FIRE_CLIENT = True # 캡처 시작 직후 자동으로 client 트래픽 발사

captured = []

def find_loopback_iface():
    """Npcap Loopback 인터페이스 탐색"""
    try:
        ifs = get_windows_if_list()
        for it in ifs:
            name = (it.get("name", "") or "")
            desc = (it.get("description", "") or "")
            
            if "Loopback" in name or "Loopback" in desc or "Npcap Loopback" in desc:
                return it.get("name")
    
    except Exception:
        pass
        
    return None

def packet_callback(pkt):
    if pkt.haslayer(TCP) and pkt.haslayer(Raw) and pkt.haslayer(IP):
        ip = pkt[IP]; tcp = pkt[TCP]
        
        if (ip.src == HOST or ip.dst == HOST) and (tcp.sport == PORT or tcp.dport == PORT):
            payload = bytes(pkt[Raw].load)
            print("[CAPTURE] Payload:", payload)
            captured.append(payload)

def fire_one_client():
    """캡처 타이밍에 맞춰 한번 로그인 트래픽을 발생시킨다."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        
        token = str(int(time.time()))
        msg = f"LOGIN|alice|{token}"
        
        s.sendall(msg.encode())
        
        _ = s.recv(4096)
        s.close()
        
        print("[AUTO] client fired:", msg)
        
    except Exception as e:
        print("[AUTO] client error:", e)

def capture_packets():
    iface = find_loopback_iface()
    
    if not iface:
        print("[!] 루프백 인터페이스를 찾지 못했습니다. Npcap 설치 시 'Support loopback traffic' 체크 여부 확인.")
        print("[*] 그래도 진행합니다(기본 인터페이스) — 캡처가 안될 수 있음.")
        iface = None # scapy 기본 선택에 맡김

    print(f"[*] {SNIFF_TIMEOUT}초 동안 TCP 캡처 시작. iface={iface}")
    
    # 캡처 시작 직후 트래픽 발생
    if AUTO_FIRE_CLIENT:
        # 서버가 이미 띄워져 있어야 함 (server.py 실행 중)
        time.sleep(0.5)
        fire_one_client()

    sniff(iface=iface,
          filter=f"tcp and host {HOST} and port {PORT}",
          prn=packet_callback,
          timeout=SNIFF_TIMEOUT,
          store=False)
          
    print(f"[*] 캡처 완료. 총 {len(captured)} 개 패킷")

def replay_packets():
    if not captured:
        print("[!] 재전송할 데이터 없음.")
        return

    for p in captured:
        print("[REPLAY-DRY] Would send:", p)
        
        if EXECUTE:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((HOST, PORT))
                s.sendall(p)
                resp = s.recv(4096)
                print("[REPLAY] Response:", resp)
                s.close()
            except Exception as e:
                print("[REPLAY][ERROR]", e)
                
    print("[*] 재연 단계 종료.")