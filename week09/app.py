import os, time, random, io
from flask import Flask, render_template, request, send_file, session, redirect, url_for, flash
from PIL import Image, ImageDraw, ImageFont, ImageFilter

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET", "devsecret_for_class")

# CAPTCHA 설정
CAPTCHA_TTL = 120 # 유효 시간 (초)
CAPTCHA_LEN = 10  # 문자열 길이
# 문자 한정
ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789" 

# --- CAPTCHA 텍스트 및 세션 관리 ---
def random_text(n=CAPTCHA_LEN):
    """지정된 길이의 무작위 텍스트를 생성합니다."""
    return "".join(random.choice(ALPHABET) for _ in range(n))

def new_challenge():
    """새로운 CAPTCHA 챌린지를 생성하고 세션에 저장합니다."""
    session["captcha"] = {"answer": random_text(), "created_at": time.time()}
    return session["captcha"]

def get_challenge():
    """현재 세션에 저장된 CAPTCHA 챌린지 정보를 가져옵니다."""
    return session.get("captcha")

def invalidate_challenge():
    """CAPTCHA 챌린지 정보를 세션에서 제거하여 무효화합니다."""
    session.pop("captcha", None)

# CAPTCHA 이미지 생성 관련
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "arial.ttf", "FreeMono.ttf"
]
def choose_font(size=42):
    for p in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(p, size=size)
        except Exception:
            continue
    return ImageFont.load_default()

def generate_captcha_image(text, width=260, height=90, rotate_range=28, line_count=6, dot_count=200):
    img = Image.new("RGB", (width, height), (255, 255, 255))
    d = ImageDraw.Draw(img)

    # 노이즈 선 추가
    for _ in range(line_count):
        a = (random.randint(0,width), random.randint(0,height))
        b = (random.randint(0,width), random.randint(0,height))
        col = (random.randint(120,200),)*3
        d.line([a,b], fill=col, width=random.randint(1,3))

    # 문자 렌더링 및 회전 적용
    spacing = width // (len(text)+2)
    base_x = spacing//2
    for i, ch in enumerate(text):
        font = choose_font(size=random.choice([40,42,44]))
        ch_img = Image.new("RGBA", (60, 60), (0,0,0,0))
        cd = ImageDraw.Draw(ch_img)
        cd.text((10, 5), ch, font=font,
            fill=(random.randint(10,120), random.randint(10,120), random.randint(10,120)))
        
        angle = random.randint(-rotate_range, rotate_range)
        ch_img = ch_img.rotate(angle, resample=Image.BICUBIC, expand=1) 
        
        x = base_x + i*spacing + random.randint(-4,6)
        y = (height - ch_img.size[1])//2 + random.randint(-6,8)
        img.paste(ch_img, (x, y), ch_img) 


    # 노이즈 점 추가
    for _ in range(dot_count):
        x, y = random.randint(0, width-1), random.randint(0, height-1)
        img.putpixel((x,y), (random.randint(100,220),)*3)

    # 이미지 필터 적용
    img = img.filter(ImageFilter.GaussianBlur(0.6))
    img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=140, threshold=2))
    return img

# --- 검증 로직 ---
def is_valid_answer(user_input: str):
    """사용자 입력을 CAPTCHA 정답과 비교하고 유효 시간을 확인합니다."""
    data = get_challenge()
    if not data:
        return False, "no-challenge"
    # 유효 시간 초과 확인
    if time.time() - data["created_at"] > CAPTCHA_TTL: 
        return False, "expired"
    # 대소문자 구분 없이 정답 비교
    if user_input.strip().upper() == data["answer"].upper(): 
        return True, "ok"
    return False, "mismatch"

# --- Flask 라우트 ---
@app.get("/")
def index():
    """메인 페이지를 렌더링합니다. 새 챌린지를 생성합니다."""
    new_challenge()
    return render_template("index.html", ts=time.time(), ttl=CAPTCHA_TTL)

@app.get("/captcha.png")
def captcha_png():
    """CAPTCHA 이미지를 생성하고 응답으로 반환합니다."""
    chal = get_challenge() or new_challenge()
    img = generate_captcha_image(chal["answer"])
    buf = io.BytesIO()
    img.save(buf, "PNG") # 이미지를 메모리 버퍼에 저장
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

@app.post("/submit")
def submit():
    """사용자가 제출한 CAPTCHA 값을 검증합니다."""
    user = request.form.get("captcha", "")
    ok, reason = is_valid_answer(user)
    if ok:
        invalidate_challenge() # 정답 처리 후 재사용 방지
        flash(" 정답입니다! 제출 성공")
    else:
        if reason == "expired":
            flash("만료되었습니다. 다시 시도하세요.")
        elif reason == "mismatch":
            flash("정답이 아닙니다. 다시 시도하세요.")
        else:
            flash("새로고침 후 다시 시도하세요.")
        new_challenge() # 실패 시 새로운 챌린지 생성
    return redirect(url_for("index"))

if __name__ == "__main__":
    # Flask 실행 전에 필요한 라이브러리 설치 필요: pip install pillow flask numpy
    app.run(debug=True)
