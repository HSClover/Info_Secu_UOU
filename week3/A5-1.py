class SimpleLSFR:
    def __init__(self, size, taps, clock_bit_index):
        self.size = size
        self.taps = taps
        self.clock_bit_index = clock_bit_index
        self.state = [0] * size
        
    def feedback(self):
        fb = 0
        for i in self.taps:
            fb ^= self.state[i]
        return fb
        
    def clock(self, input_bit=0):
        fb = self.feedback() ^ input_bit
        out = self.state[-1]
        self.state = [fb] + self.state[:-1]
        return out
    
    def get_clock_bit(self):
        return self.state[self.clock_bit_index]

    def majority(a, b, c):
        count = a + b + c
        if count >= 2:
            return 1
        else:
            return 0
        
class SimpleA5:
    def __init__(self, key, frame):
        self.key = key
        self.frame = frame
        self.x, self.y, self.z = self.init_registers()
    
    def init_registers(self):
        self.x = SimpleLSFR(size=5, taps=[2, 4], clock_bit_index=2)
        self.y = SimpleLSFR(size=6, taps=[1, 5], clock_bit_index=3)
        self.z = SimpleLSFR(size=7, taps=[1, 5, 6], clock_bit_index=4)
        
        for i in range(16):
            key_bit = (self.key >> i) & 1
            self.x.clock(input_bit=key_bit)
            self.y.clock(input_bit=key_bit)
            self.z.clock(input_bit=key_bit)

        for i in range(8):
            frame_bit = (self.frame >> i) & 1
            self.x.clock(input_bit=frame_bit)
            self.y.clock(input_bit=frame_bit)
            self.z.clock(input_bit=frame_bit)

        for _ in range(10):
            self.get_keystream_bit()
        
        return self.x, self.y, self.z

    def get_keystream_bit(self):
        majority_result = SimpleLSFR.majority(self.x.get_clock_bit(), self.y.get_clock_bit(), self.z.get_clock_bit())
        
        if self.x.get_clock_bit() == majority_result:
            self.x.clock()
        if self.y.get_clock_bit() == majority_result:
            self.y.clock()
        if self.z.get_clock_bit() == majority_result:
            self.z.clock()

        return self.x.state[4] ^ self.y.state[5] ^ self.z.state[6]

    def get_keystream(self, nbits):
        keystream = 0
        for _ in range(nbits):
            keystream = (keystream << 1) | self.get_keystream_bit()

        return keystream

# ===== 테스트 ======
a5 = SimpleA5(0xBEEF, 0x3A)
keystream = a5.get_keystream(8)
print("키스트림:", format(keystream, '08b'))

#   kc = 0xBEEF
#   FN = 0x3A
#   워밍업 10회
#   Sbit : X[4], y[5], z[6]