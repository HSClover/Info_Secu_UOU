from flask import Flask
app = Flask(__name__)
@app.route("/")
def index():
    return "<h1>Hello, Flask!</h1>"
if __name__ == "__main__":
    app.run(debug=True)


import os, time, random, io
from flask import Flask, render_template, request, send_file, session, redirect, url_for, flash

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET", "devsecret_for_class")

CAPTCHA_TTL = 120
CAPTCHA_LEN = 5
ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789" # 모호문자 제거(I,l,O,0)

def random_text(n=CAPTCHA_LEN):
    return "".join(random.choice(ALPHABET) for _ in range(n))

def new_challenge():
    session["captcha"] = {"answer": random_text(), "created_at": time.time()}
    return session["captcha"]

def get_challenge():
    return session.get("captcha")

def invalidate_challenge():
    session.pop("captcha", None)

@app.get("/")
def index():
    new_challenge()
    return render_template("index.html", ts=time.time(), ttl=CAPTCHA_TTL)

if __name__ == "__main__":
    app.run(debug=True)



from PIL import Image, ImageDraw, ImageFont, ImageFilter

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

def generate_captcha_image(text, width=260, height=90, rotate_range=28, line_count=6, dot_count=400):
    img = Image.new("RGB", (width, height), (255, 255, 255))
    d = ImageDraw.Draw(img)
    for _ in range(line_count):
        a = (random.randint(0,width), random.randint(0,height))
        b = (random.randint(0,width), random.randint(0,height))
        col = (random.randint(120,200),)*3
        d.line([a,b], fill=col, width=random.randint(1,3))
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


    for _ in range(dot_count):
        x, y = random.randint(0, width-1), random.randint(0, height-1)
        img.putpixel((x,y), (random.randint(100,220),)*3)

    img = img.filter(ImageFilter.GaussianBlur(0.6))
    img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=140, threshold=2))
    return img

@app.get("/captcha.png")
def captcha_png():
    chal = get_challenge() or new_challenge()
    img = generate_captcha_image(chal["answer"])
    buf = io.BytesIO(); img.save(buf, "PNG"); buf.seek(0)
    return send_file(buf, mimetype="image/png")


def is_valid_answer(user_input: str):
    data = get_challenge()
    if not data:
        return False, "no-challenge"
    if time.time() - data["created_at"] > CAPTCHA_TTL:
        return False, "expired"
    if user_input.strip().upper() == data["answer"].upper():
        return True, "ok"
    return False, "mismatch"

@app.post("/submit")
def submit():
    user = request.form.get("captcha", "")
    ok, reason = is_valid_answer(user)
    if ok:
        invalidate_challenge() # 재사용 방지
        flash(" 정답")
    else:
        if reason == "expired":
            flash("만료되었습니다. 다시 시도하세요.")
        elif reason == "mismatch":
            flash("정답이 아닙니다. 다시 시도하세요.")
        else:
            flash("새로고침 후 다시 시도하세요.")
        new_challenge()
    return redirect(url_for("index"))