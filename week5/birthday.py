# n = 50
# persent = 1
# minus = 1
# 
# for i in range(1,n+1):
    # minus *= ((366-i)/365)
    # persent = 1-minus
    # print(f"{i}명일 때, {persent*100:.5f}%")
    
import hashlib
import os

# 주요 숫자 설정
BIT = 16
BYTE = BIT // 2
MAX = 50

def birthday():
    hash_pre = set()
    attempt = 0
    
    while True:
        attempt += 1
        msg = os.urandom(16)
        hash = hashlib.sha256(msg).digest()
        
        prefix = hash[:BYTE]
        
        if prefix in hash_pre:
            return attempt
        else:
            hash_pre.add(prefix)

crash_attempt = []
for i in range(MAX):
    attempt = birthday()
    crash_attempt.append(attempt)
    print(f"[{i+1}/{max}] 충돌까지 시도 횟수 : {attempt}")
    
average_attempt = sum(crash_attempt) / MAX
thr_attempt = 2**(BIT/2)

print(f"=== 총 {MAX}회 ===\n평균 충올 발생 시도 : {average_attempt:.3f}\n이론상 횟수 : {thr_attempt:.0f}")