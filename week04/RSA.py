# RSA 실습 (정답 버전, 각 인자별 설명 포함)

from math import gcd

def egcd(a: int, b: int):
    """
    확장 유클리드 알고리즘 (Extended Euclidean Algorithm)
    입력:
        a (int): 정수
        b (int): 정수
    출력:
        (g, x, y): gcd(a,b)=g와, g = a*x + b*y 를 만족하는 (x,y)
    """
    if (b==0):
        return (a,1,0)
    g, x1, y1 = egcd(b, a%b)
    return (g,y1, x1-(a//b)*y1)


def modinv(a: int, m: int) -> int:
    """
    모듈러 역원 (modular inverse) 계산
    목적:
        a*d ≡ 1 (mod m) 를 만족하는 d를 찾는다.
    입력:
        a (int): 역원을 구하고자 하는 수 (예: e)
        m (int): 법(modulus), RSA에서는 φ(n)
    출력:
        d (int): a의 역원
    예외:
        gcd(a, m) != 1 인 경우 ValueError 발생 (역원이 존재하지 않음)
    """
    g, x, _ = egcd(a, m)
    if g != 1:
        raise ValueError(f"역원이 존재하지 않습니다: a={a}, m={m}, gcd={g}")
    # 코드 작성
    return (a ** (m-2) )


def generate_keys(p: int, q: int, e: int = 7):
    """
    RSA 키 생성
    입력:
        p (int): 소수
        q (int): 소수
        e (int): 공개 지수 (φ(n)과 서로소, 기본값 7)
    출력:
        (public_key, private_key)
        public_key  = (n, e)
        private_key = (n, d)
    설명:
        1) n = p * q
        2) φ(n) = (p-1)*(q-1)
        3) gcd(e, φ(n)) == 1 확인
        4) d = e^-1 mod φ(n) 계산
    """
    if p == q:
        raise ValueError("p와 q는 서로 다른 소수여야 합니다.")
    # 코드 작성
    n = p*q
    phi = (p-1)*(q-1)
    
    if gcd(e, phi) != 1:
        raise ValueError(f"e와 φ(n)은 서로소여야 합니다. (e={e}, φ={phi})")
    # 코드 작성
    g, x, y = egcd(e, phi)
    d = x%phi
    return (n,e), (n,d)


def encrypt(m: int, public_key: tuple[int, int]) -> int:
    """
    RSA 암호화
    입력:
        m (int): 평문 메시지 (0 <= m < n 이어야 함)
        public_key (tuple): (n, e)
            n: 모듈러스
            e: 공개 지수
    출력:
        c (int): 암호문
    수식:
        c = m^e mod n
    """
    n, e = public_key
    if not (0 <= m < n):
        raise ValueError(f"메시지 m은 0 <= m < n 이어야 합니다. (m={m}, n={n})")
    #코드 작성
    c = m**e % n
    return c


def decrypt(c: int, private_key: tuple[int, int]) -> int:
    """
    RSA 복호화
    입력:
        c (int): 암호문 (0 <= c < n 이어야 함)
        private_key (tuple): (n, d)
            n: 모듈러스
            d: 개인 지수
    출력:
        m (int): 복호화된 평문 메시지
    수식:
        m = c^d mod n
    """
    n, d = private_key
    if not (0 <= c < n):
        raise ValueError(f"암호문 c는 0 <= c < n 이어야 합니다. (c={c}, n={n})")
    # 코드 작성
    m = c**d %n
    return int(m)

# ========================
# 데모 실행
# ========================

def demo_keygen():
    public_key, private_key = generate_keys(17, 11, e=7)
    print("공개키 (n, e):", public_key)
    print("개인키 (n, d):", private_key)


def demo_integer():
    public_key, private_key = generate_keys(17, 11, e=7)
    message = 88  # 0 <= m < n(=187) 범위 내
    cipher = encrypt(message, public_key)
    plain = decrypt(cipher, private_key)
    print(f"[정수] 원본={message}, 암호문={cipher}, 복호화={plain}")


def demo_text():
    public_key, private_key = generate_keys(17, 11, e=7)
    text = "HI"
    nums = [ord(ch) for ch in text]  # 문자열 → 아스키 코드 변환
    cipher_nums = [encrypt(m, public_key) for m in nums]
    plain_nums = [decrypt(c, private_key) for c in cipher_nums]
    decrypted_text = "".join(chr(x) for x in plain_nums)
    print(f"[문자열] 원문={text}")
    print(f"[문자열] 암호문={cipher_nums}")
    print(f"[문자열] 복호화={decrypted_text}")


def run_all():
    print("=== 1) 키 생성 ===")
    demo_keygen()
    print("\n=== 2) 정수 메시지 암/복호화 ===")
    demo_integer()
    print("\n=== 3) 문자열 암/복호화 ===")
    demo_text()


if __name__ == "__main__":
    run_all()
