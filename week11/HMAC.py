import hmac, hashlib, secrets, json, time, sys
from typing import Tuple

SHARED_SECRET = b"alice-and-bob-super-secret"


import hmac
import hashlib
import json

def hmac_sha256(key: bytes, msg: bytes) -> bytes:
    return hmac.new(key, msg, hashlib.sha256).digest()

def pretty(obj) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False)


WIRE_LOG = []  # (dir, msg): "C->S", "S->C", "A(C)->S", "Attacker Replay"

def client_static_token_login(username: str = "alice") -> dict:
    # 토큰 생성: SHARED_SECRET과 "LOGIN" 고정 메시지를 사용하여 HMAC 토큰 생성. -> 고정 토큰
    token = hmac_sha256(SHARED_SECRET, b"LOGIN")

    # 클라이언트가 서버로 전송할 로그인 메시지 생성
    msg = {"type": "login_static", "username": username, "token_hex": token.hex()}

    # 통신 기록(WIRE_LOG)에 메시지 기록
    WIRE_LOG.append(("C->S", msg))

    # 생성된 메시지 반환
    return msg

from typing import Tuple

def server_static_token_check(msg: dict) -> Tuple[bool, str]:
    if msg.get("type") != "login_static":
        return False, "잘못된 메시지 타입"
    
    exp = hmac_sha256(SHARED_SECRET, b"LOGIN").hex()
    ok = (msg.get("token_hex") == exp)
    
    return ok, ("인증성공(취약: 리플레이 가능)" if ok else "인증실패")


def run_lab_static():
    WIRE_LOG.clear()
    
    msg = client_static_token_login()
    
    ok, s = server_static_token_check(msg)
    print("[정상 시도] ", s)
    
    replay = WIRE_LOG[0][1]
    WIRE_LOG.append(("Attacker Replay", replay))
    
    ok_r, s_r = server_static_token_check(replay)
    print("[리플레이] ", s_r)
    
    print("\n[전송 기록]\n", pretty(WIRE_LOG))


import secrets
import time

def server_issue_nonce() -> dict:
    nonce = secrets.token_hex(16)  # 128-bit hex
    msg = {"type": "challenge", "nonce": nonce, "ts": time.time()}
    WIRE_LOG.append(("S->C", msg))
    return msg

#from typing import Tuple, dict, int, bool, float
import time

# WIRE_LOG 변수 및 기타 종속성 (hmac_sha256, SHARED_SECRET, pretty 등)은 별도로 정의되어 있어야 합니다.

def _last_challenge():
    for d in reversed(WIRE_LOG):
        if d[1].get("type") == "challenge":
            return d[1]
    return None

def _is_fresh(chal: dict, freshness_sec: int = 30) -> bool:
    return (time.time() - chal["ts"]) <= freshness_sec

def server_verify_response(reply_msg: dict, freshness_sec: int = 30) -> Tuple[bool, str]:
    chal = _last_challenge()
    if not chal:
        return False, "서버에 난스가 없음"
    
    if not _is_fresh(chal, freshness_sec):
        return False, "난스 만료"
    
    exp_mac = hmac_sha256(SHARED_SECRET, chal["nonce"].encode()).hex()
    ok = (reply_msg.get("mac_hex") == exp_mac)
    
    return ok, ("인증성공(리플레이 방어)" if ok else "인증실패")

def client_respond_nonce(challenge_msg: dict, username: str = "alice") -> dict:
    nonce = challenge_msg["nonce"]
    mac = hmac_sha256(SHARED_SECRET, nonce.encode())
    
    reply = {"type": "response", "username": username, "nonce": nonce, "mac_hex": mac.hex()}
    WIRE_LOG.append(("C->S", reply))
    return reply

def run_lab_nonce(freshness_sec: int = 1, delay_before_replay_sec: float = 2.0):
    WIRE_LOG.clear()
    
    ch = server_issue_nonce()
    rep = client_respond_nonce(ch)
    
    ok, s = server_verify_response(rep, freshness_sec=freshness_sec)
    print("[정상 시도] ", s)
    
    if delay_before_replay_sec > 0:
        time.sleep(delay_before_replay_sec)
    
    ok_r, s_r = server_verify_response(rep, freshness_sec=freshness_sec) # 같은 응답 재연
    print("[리플레이] ", s_r)
    
    print("\n[전송 기록]\n", pretty(WIRE_LOG))

def derive_session_key(nonce: str) -> bytes:
    return hmac_sha256(SHARED_SECRET, f"session:{nonce}".encode())

def attacker_proxy_attempt() -> Tuple[bool, str]:
    challenge = server_issue_nonce()
    
    fake_mac = hashlib.sha256(b"wrong").hexdigest()  # 비밀키 없이 임의의 값
    
    forged = {"type": "response", "username": "alice", "nonce": challenge["nonce"], "mac_hex": fake_mac}
    
    WIRE_LOG.append(("A(C)->S", forged))
    
    ok, msg = server_verify_response(forged)
    return ok, msg

def run_lab_proxy():
    WIRE_LOG.clear()
    
    ok, s = attacker_proxy_attempt()
    print("[프록시 공격] ", s)
    
    print("\n[전송 기록]\n", pretty(WIRE_LOG))

def MAIN_RUN(step: int = 1):
    if step == 1:
        run_lab_static()
    elif step == 2:
        run_lab_nonce(freshness_sec=30, delay_before_replay_sec=0.0)
    elif step == 3:
        run_lab_proxy()
    else:
        print("step은 1, 2, 3 중 선택")

if __name__ == "__main__":
    MAIN_RUN(step=2)




