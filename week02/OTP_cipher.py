import random

# 원문
text = "heilhitler"

#bit table
bit_table = {"e":0b000,"h":0b001,"i":0b010,"k":0b011,"l":0b100,"r":0b101,"s":0b110,"t":0b111}

keys = []
text_bits = []
cyripto = []

# 길이가 같아서 한번에 할 수 있을 것 같음
# # 랜덤 3비트 키 생성 (0~7)
# for _ in range(len(text)):
    # key.append(random.getrandbits(3))  # 정수 상태로 저장
# 
# # 원문을 3비트 정수로 변환
# for c in text:
    # text_bits.append(bit_table[c])
# 
# # XOR 암호화
# for i in range(len(text)):
    # cyripto.append(key[i] ^ text_bits[i])  # XOR 연산
    
# 재문자화를 위한 역dict생성
rbit_table = {v: k for k, v in bit_table.items()}


for c in text:
    key = random.getrandbits(3)
    tbit = bit_table[c]
    xor = key^tbit
    
    keys.append(key)
    text_bits.append(tbit)
    cyripto.append(rbit_table.get(xor))
    
# 출력
print("원문 : ", text)
print("암호문 : ", "".join(cyripto))

print("Key(bin)) : ", [format(k, '03b') for k in keys])
print("Text(bin) :", [format(t, '03b') for t in text_bits])
print("cyripto(bin) :", [format(bit_table.get(c,0), '03b') if c in bit_table else "???" for c in cyripto])
