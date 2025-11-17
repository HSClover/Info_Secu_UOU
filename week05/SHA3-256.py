import hashlib

text1 = "hello"
text2 = "hello!"

hash1 = hashlib.sha3_256(text1.encode()).hexdigest()
hash2 = hashlib.sha3_256(text2.encode()).hexdigest()

print(f"Text1: {text1} => Hash: {hash1}")
print(f"Text2: {text2} => Hash: {hash2}")