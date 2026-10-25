#!/usr/bin/env python3
"""Create a Japanese vertical narrated short with VOICEVOX and FFmpeg."""
import json
import os
import subprocess
import time
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
BASE = os.environ.get("VOICEVOX_URL", "http://127.0.0.1:50021").rstrip("/")
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
WIDTH, HEIGHT = 720, 1280
TARGET_SECONDS = int(os.environ.get("TARGET_SECONDS", "30"))


def request(path, data=None):
    body = None if data is None else json.dumps(data, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(BASE + path, data=body, method="POST" if body is not None else "GET")
    if body is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=120) as response:
        return response.read()


def synthesize(text, speaker, output):
    params = urllib.parse.urlencode({"text": text, "speaker": speaker})
    req = urllib.request.Request(BASE + "/audio_query?" + params, data=b"", method="POST")
    with urllib.request.urlopen(req, timeout=120) as response:
        query = json.loads(response.read())
    query["speedScale"] = 1.4
    params = urllib.parse.urlencode({"speaker": speaker})
    output.write_bytes(request("/synthesis?" + params, query))


def wrap_text(draw, text, font, max_width=590):
    result = []
    for paragraph in text.split("\n"):
        line = ""
        for char in paragraph:
            trial = line + char
            if line and draw.textbbox((0, 0), trial, font=font)[2] > max_width:
                result.append(line)
                line = char
            else:
                line = trial
        if line:
            result.append(line)
    return result


def draw_scene(draw, scene, accent):
    # Original vector illustrations: no third-party imagery or paid API.
    if scene == "train":
        draw.rounded_rectangle((80, 310, 640, 860), radius=65, fill=(54, 104, 142), outline=accent, width=9)
        draw.rounded_rectangle((125, 390, 595, 650), radius=22, fill=(127, 186, 202))
        draw.line((360, 390, 360, 650), fill=(20, 56, 82), width=14)
        draw.ellipse((150, 715, 205, 770), fill=(255, 233, 170))
        draw.ellipse((515, 715, 570, 770), fill=(255, 233, 170))
        draw.line((115, 895, 605, 895), fill=accent, width=13)
    elif scene == "road":
        draw.polygon([(255, 275), (465, 275), (720, 1120), (0, 1120)], fill=(52, 80, 101))
        for y in range(350, 1080, 145):
            draw.rounded_rectangle((350, y, 370, y + 70), radius=8, fill=(255, 221, 122))
        draw.rounded_rectangle((145, 740, 575, 975), radius=50, fill=(47, 164, 179))
        draw.rounded_rectangle((205, 770, 515, 840), radius=18, fill=(170, 218, 227))
        for x in (240, 485):
            draw.ellipse((x - 48, 935, x + 48, 1031), fill=(19, 34, 51))
    elif scene == "clock":
        draw.ellipse((120, 330, 600, 810), fill=(56, 103, 131), outline=accent, width=19)
        draw.line((360, 570, 360, 405), fill="white", width=17)
        draw.line((360, 570, 485, 635), fill="white", width=17)
        draw.ellipse((340, 550, 380, 590), fill=accent)
        for angle in range(0, 360, 30):
            import math
            a = math.radians(angle)
            x = 360 + 205 * math.sin(a)
            y = 570 - 205 * math.cos(a)
            draw.ellipse((x-7, y-7, x+7, y+7), fill="white")
    elif scene == "phone":
        draw.rounded_rectangle((185, 250, 535, 1030), radius=54, fill=(30, 45, 65), outline=accent, width=13)
        draw.rounded_rectangle((212, 325, 508, 935), radius=18, fill=(58, 104, 141))
        draw.rounded_rectangle((287, 280, 433, 296), radius=8, fill=(145, 175, 192))
        for x, y in ((250, 380), (355, 380), (250, 485), (355, 485)):
            draw.rounded_rectangle((x, y, x + 75, y + 75), radius=17, fill=(102, 194, 196))
        draw.ellipse((344, 966, 376, 998), outline=(180, 215, 220), width=4)
    elif scene == "calendar":
        draw.rounded_rectangle((115, 340, 605, 880), radius=35, fill=(50, 91, 120), outline=accent, width=12)
        draw.rectangle((125, 455, 595, 465), fill=accent)
        for row in range(4):
            for col in range(5):
                x, y = 165 + col * 87, 510 + row * 82
                draw.rounded_rectangle((x, y, x + 48, y + 48), radius=8, fill=(137, 191, 206))
    elif scene == "battery":
        draw.rounded_rectangle((125, 375, 570, 795), radius=42, outline=accent, width=18)
        draw.rounded_rectangle((570, 515, 600, 655), radius=12, fill=accent)
        for j in range(4):
            draw.rounded_rectangle((155 + j * 95, 420, 225 + j * 95, 750), radius=16,
                                   fill=(73, 200 - j * 24, 150 - j * 18))
    elif scene == "hourglass":
        draw.line((180, 315, 540, 315), fill=accent, width=22)
        draw.line((180, 900, 540, 900), fill=accent, width=22)
        draw.polygon([(215, 345), (505, 345), (360, 590)], fill=(90, 159, 185))
        draw.polygon([(360, 620), (505, 865), (215, 865)], fill=(219, 185, 105))
        draw.line((360, 590, 360, 740), fill=(255, 223, 141), width=13)
    elif scene == "people":
        for x, y, r in ((175, 430, 48), (360, 350, 62), (545, 430, 48)):
            draw.ellipse((x-r, y-r, x+r, y+r), fill=(113, 187, 201))
            draw.rounded_rectangle((x-r-35, y+r+18, x+r+35, y+r+245), radius=50, fill=(46, 112, 142))
    elif scene == "chart":
        for i, height in enumerate((180, 310, 440, 585)):
            x = 100 + i * 142
            draw.rounded_rectangle((x, 960-height, x+92, 960), radius=12,
                                   fill=(68 + i * 12, 156 + i * 16, 178))
        draw.line((90, 970, 650, 970), fill=accent, width=12)
    elif scene == "sunrise":
        draw.ellipse((205, 330, 515, 640), fill=(255, 191, 104))
        draw.rectangle((0, 680, 720, 1030), fill=(40, 90, 120))
        for x, h in ((35, 170), (145, 260), (270, 140), (395, 320), (535, 215)):
            draw.rectangle((x, 680-h, x+100, 900), fill=(33, 68, 100))
    elif scene == "shoes":
        for j, (x, y) in enumerate(((100, 345), (365, 450), (120, 590))):
            draw.ellipse((x+8, y+65, x+205, y+170), fill=(28, 46, 64))
            draw.polygon([(x+10, y+110), (x+65, y+32), (x+140, y+55),
                          (x+162, y+110), (x+220, y+135), (x+220, y+165),
                          (x+15, y+165)], fill=(69+j*30, 172-j*15, 188))
            draw.line((x+15, y+160, x+215, y+160), fill=(240, 239, 218), width=11)
            for k in range(3):
                draw.line((x+90+k*17, y+83, x+106+k*17, y+94), fill="white", width=5)
    elif scene == "shoe_line":
        draw.line((35, 670, 685, 670), fill=accent, width=12)
        for j in range(5):
            x=45+j*135
            draw.polygon([(x, 600), (x+28, 555), (x+62, 575),
                          (x+75, 613), (x+105, 630), (x+105, 651), (x, 651)],
                         fill=(74, 177, 188))
            draw.line((x, 650, x+105, 650), fill="white", width=7)
    elif scene == "earth":
        draw.ellipse((130, 295, 590, 755), fill=(53, 136, 186), outline=accent, width=12)
        draw.polygon([(230, 360), (330, 330), (390, 405), (340, 490),
                      (400, 540), (320, 655), (245, 570), (260, 470)],
                     fill=(74, 182, 136))
        draw.polygon([(455, 340), (535, 415), (490, 480), (540, 550),
                      (465, 650), (420, 570), (445, 490)], fill=(74, 182, 136))
        draw.arc((80, 260, 640, 790), 15, 345, fill=(255, 218, 112), width=15)
    elif scene == "japan":
        draw.polygon([(465, 300), (490, 340), (462, 400), (442, 475),
                      (405, 550), (355, 610), (302, 685), (265, 720),
                      (240, 685), (280, 640), (340, 575), (380, 495),
                      (420, 410)], fill=(77, 188, 155))
        draw.ellipse((180, 740, 255, 815), fill=(77, 188, 155))
    elif scene == "question":
        question_font = ImageFont.truetype(FONT, 370)
        draw.text((245, 280), "？", font=question_font, fill=accent)
    elif scene == "office":
        for x, top, width in ((55, 480, 185), (265, 300, 190), (475, 405, 185)):
            draw.rectangle((x, top, x + width, 1000), fill=(46, 92, 120), outline=accent, width=4)
            for wx in range(x + 25, x + width - 10, 55):
                for wy in range(top + 45, 960, 75):
                    draw.rectangle((wx, wy, wx + 28, wy + 36), fill=(127, 189, 204))
    else:
        for x, y, r in ((155, 460, 95), (525, 590, 130), (300, 800, 65)):
            draw.ellipse((x-r, y-r, x+r, y+r), outline=accent, width=12)


def make_card(text, number, total, output, scene="clock", headline=""):
    image = Image.new("RGB", (WIDTH, HEIGHT), (13, 26, 48))
    draw = ImageDraw.Draw(image)
    accent = (75, 224, 196)
    draw_scene(draw, scene, accent)
    # Topic-specific environmental details: perspective, texture and labels.
    if scene == "earth":
        for ring in range(3):
            inset = ring * 25
            draw.arc((65+inset, 250+inset, 655-inset, 825-inset),
                     195, 345, fill=(69+ring*30, 174+ring*12, 203), width=4)
        draw.ellipse((545, 430, 590, 475), fill=(255, 220, 115))
        draw.text((90, 660), "EARTH / 40,000 km", font=ImageFont.truetype(FONT, 25),
                  fill=(193, 227, 235))
    elif scene == "japan":
        for x,y in ((155,420),(565,480),(135,660),(545,690)):
            draw.ellipse((x-24,y-24,x+24,y+24), fill=(59, 160, 181))
            draw.ellipse((x-9,y-35,x+9,y-17), fill=(255, 224, 146))
        draw.text((120, 825), "POPULATION / 120,000,000",
                  font=ImageFont.truetype(FONT, 23), fill=(196, 230, 235))
    elif scene in ("shoes", "shoe_line"):
        for y in (380, 420, 460):
            draw.line((40,y,680,y), fill=(25, 60, 78), width=2)
        for x in range(60,680,60):
            draw.line((x,370,x,700), fill=(25, 60, 78), width=2)
        draw.text((85, 710), "1 SHOE = 25 cm", font=ImageFont.truetype(FONT, 27),
                  fill=(255, 216, 120))
    elif scene == "question":
        for x,y in ((115,410),(565,440),(130,640),(590,680)):
            draw.ellipse((x-14,y-14,x+14,y+14), fill=(255, 215, 112))
    # Keep visuals above the caption, not hidden behind an oversized text box.
    draw.rounded_rectangle((28, 735, 692, 1065), radius=32, fill=(11, 24, 43))
    draw.rounded_rectangle((42, 93, 678, 105), radius=6, fill=accent)
    small = ImageFont.truetype(FONT, 28)
    draw.text((53, 131), "ラテラルシンキング", font=small, fill=accent)
    if headline:
        font = ImageFont.truetype(FONT, 100 if len(headline) <= 8 else 65)
        bbox = draw.textbbox((0, 0), headline, font=font)
        draw.text(((WIDTH - (bbox[2]-bbox[0]))//2, 202), headline, font=font,
                  fill=(255, 222, 115), stroke_width=3, stroke_fill=(15, 29, 49))
    font_size = 56
    while True:
        font = ImageFont.truetype(FONT, font_size)
        lines = wrap_text(draw, text, font, max_width=585)
        line_height = font_size + 17
        if len(lines) * line_height <= 280 or font_size <= 30:
            break
        font_size -= 2
    y = 900 - len(lines) * line_height // 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        x = (WIDTH - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), line, font=font, fill="white")
        y += line_height
    draw.text((54, 1125), f"{number:02d} / {total:02d}", font=small, fill=accent)
    draw.rounded_rectangle((54, 1190, 666, 1201), radius=5, fill=(48, 76, 95))
    draw.rounded_rectangle((54, 1190, 54 + int(612*number/total), 1201), radius=5, fill=accent)
    credit = ImageFont.truetype(FONT, 20)
    draw.text((380, 1128), "VOICEVOX:春日部つむぎ", font=credit, fill=(165, 184, 195))
    image.save(output)


def run(*args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL)


def duration(path):
    result = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path)
    ], text=True)
    return float(result.strip())


def main():
    script = json.loads((ROOT / "scripts" / "script.json").read_text(encoding="utf-8"))
    speaker = int(os.environ.get("VOICEVOX_SPEAKER", "8"))
    segments = script["segments"]
    if not 1 <= len(segments) <= 12:
        raise ValueError("segments must contain 1 to 12 entries")
    for _ in range(40):
        try:
            request("/version")
            break
        except Exception:
            time.sleep(3)
    else:
        raise RuntimeError("VOICEVOX engine did not become ready")
    work = ROOT / "build"
    out = ROOT / "output"
    work.mkdir(exist_ok=True)
    out.mkdir(exist_ok=True)
    clips = []
    for i, segment in enumerate(segments, 1):
        text = str(segment["text"]).strip()
        if not text or len(text) > 140:
            raise ValueError(f"Invalid text in segment {i}")
        wav = work / f"{i:02}.wav"
        png = work / f"{i:02}.png"
        mp4 = work / f"{i:02}.mp4"
        synthesize(text, speaker, wav)
        make_card(text, i, len(segments), png, segment.get("scene", "clock"), segment.get("headline", ""))
        seconds = duration(wav) + 0.45
        run("ffmpeg", "-y", "-loop", "1", "-framerate", "30", "-i", str(png),
            "-i", str(wav), "-filter_complex", "[0:v]scale=792:1408,zoompan=z='min(zoom+0.0012,1.15)':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':d=1:s=720x1280:fps=30,format=yuv420p[v];[1:a]apad[a]",
            "-map", "[v]", "-map", "[a]", "-t", f"{seconds:.3f}",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac",
            "-b:a", "128k", "-ar", "44100", str(mp4))
        clips.append(mp4)
    manifest = work / "concat.txt"
    manifest.write_text("".join(f"file '{clip.resolve()}'\n" for clip in clips), encoding="utf-8")
    final = out / "lateral-short.mp4"
    run("ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(manifest),
        "-c", "copy", "-movflags", "+faststart", str(final))
    # Normalize the completed clip to precisely 20 seconds at 30 fps.
    # Speed both audio and video together, rather than cutting narration.
    raw_seconds = duration(final)
    factor = raw_seconds / TARGET_SECONDS
    normalized = out / "normalized.mp4"
    run("ffmpeg", "-y", "-i", str(final),
        "-filter_complex",
        f"[0:v]setpts=(PTS-STARTPTS)/{factor:.8f},fps=30,trim=duration={TARGET_SECONDS},setpts=PTS-STARTPTS[v];"
        f"[0:a]atempo={factor:.8f},atrim=duration={TARGET_SECONDS},apad=whole_dur={TARGET_SECONDS}[a]",
        "-map", "[v]", "-map", "[a]", "-t", str(TARGET_SECONDS),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "160k",
        "-movflags", "+faststart", str(normalized))
    normalized.replace(final)
    print(f"Video ready: {final} ({duration(final):.1f} seconds, 30 fps)")


if __name__ == "__main__":
    main()
