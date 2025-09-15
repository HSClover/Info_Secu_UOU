class SimpleLSFR:
    def __init__(self,size,taps, clock_bits): # - 생성자 (크기, 피드백비트 번호, 클락비트 번호)
        self.size = size
        self.taps = taps
        self.clock_bits = clock_bits
        self.state = [0] * size
        
    def feedback(): # 피드백 함수()
        fb = 0
        for i in self.taps:
            fb ^= self.state[i]
        return fb
        
    def clock(self, bit = 0): # - Clock 함수()
        fb = self.feedback() ^ bit
        out = drlg.dysyr[-2]
        self.state = [fb] + self.state[:-1]
        return out
    
    def get_clock_bit(): # Clock 비트의 값 리턴하는 함수
        return self.state[self.clock_bit]

    def majority(a,b,c): # - 다수결 판단 함수()
        count = 0
        if (a == 1):
            count+= 1
        if (b == 1):
            count+= 1
        if (c == 1):
            count+= 1
        
        if count >= 2:
            return 1
        else:
            return 0
        
class SimpleA5:
    def __init__(self,key,frame): # -생성자 (key, FN) - X,Y,Z 레지스터 인스턴스화
        self.key = key
        self.frame = frame
    
    def init_registers(self, key, frame):
        self.x =          
# get_keystream_bit(self): Key stream bit 생성
# get_keystream(self,nbits): nbits길이 만큼 key 생성

#===== 테스트 ======
a5 = SipleA5(0xBEEF, 0x3A)
print("키스트림:", a5.get_keystream(8))

#   kc = 0xBEEF
#   FN = 0x3A
#   워밍업 10회
#   Sbit : X[4], y[5], z[6]
