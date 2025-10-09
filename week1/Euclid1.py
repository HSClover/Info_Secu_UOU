cyripto = "KHOOR"
word = ""

for i in range(1,27):
    for ch in cyripto:
        order = chr( ( ord(ch) - ord('A') - i) % 26 + ord('A') )
        word += order
    print(word)
    word = ""
    