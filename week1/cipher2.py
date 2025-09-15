# 문제
cyripto = "YMNX NX F XNRUQJ JCFRUQJ. KWJVBJD TZFQNXNX HFS MJQU YT GWJFP HNUMJWZX"

# 영어빈도분석
order_to_frequency = "EARIOTNS"

# 가장 많이 등장하는 알파벳 찾기
counts = {}

for ch in cyripto:       
    if ch.isalpha():         
        counts[ch] = counts.get(ch, 0) + 1
        
most_common_char = max(counts, key=counts.get)

# 빈도분석 단어와 비교해서 가장 많이 등장하는 알파벳을 가지고 해석하기
for target in order_to_frequency:
    shift = (ord(most_common_char) - ord(target)) % 26
    decode = ""
    
    for ch in cyripto:
        if ch.isalpha():
            decode += chr( (ord(ch) - ord('A') - shift) % 26 + ord('A'))
        else:
            decode += ch
    # 답 출력
    print(decode)