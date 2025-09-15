import random

# 코드북 암호와 복호화를 위한 리버스 코드북
codebook = {"attack":1234,"dawn":5678,"meet":9101,"secret":1121}
reverse_codebook = {v: k for k, v in codebook.items()}

# 문장 입력 받음
sentence = input("문장을 입력하시오 : ").split()
codes = [codebook.get(word, 0) for word in sentence]

# 암호 난수 생성
add_seq = [random.randint(1,9999) for _ in range(len(sentence))]
print("Additive Sequence : ", add_seq)

# 암호 더하기
added_codes = [c + s for c, s in zip(codes, add_seq)]

# 암호문
print("cyripto : ",added_codes)

# 복호화 시작
unadd_codes = [c - s for c, s in zip(added_codes, add_seq)]

# 리버스 코드북에서 찾아서 저장
decrypted_text_list = [reverse_codebook.get(code, "?") for code in unadd_codes]

# string 변수로 만듦
decrypted_text = " ".join(decrypted_text_list)

# 복호화된 원문
print("decrypted_text : ",decrypted_text)