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
    query["speedScale"] = 1.18
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
    draw = ImageDraw.Draw(image, "RGB")
    accent = (75, 224, 196)
    draw_scene(draw, scene, accent)
    # Dim illustration behind opaque subtitle panel for readability.
    draw.rounded_rectangle((35, 420, 685, 850), radius=38, fill=(12, 23, 42))
    draw.rounded_rectangle((42, 92, 678, 103), radius=5, fill=accent)
    small = ImageFont.truetype(FONT, 29)
    draw.text((54, 132), "ラテラルシンキング", font=small, fill=accent)
    font_size = 59
    while True:
        font = ImageFont.truetype(FONT, font_size)
        lines = wrap_text(draw, text, font)
        line_height = font_size + 15
        if len(lines) * line_height <= 340 or font_size <= 30:
            break
        font_size -= 2
    y = 635 - len(lines) * line_height // 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        x = max(52, (WIDTH - (bbox[2] - bbox[0])) // 2)
        draw.text((x, y), line, font=font, fill="white")
        y += line_height
    draw.text((54, 1135), f"{number:02d} / {total:02d}", font=small, fill=accent)
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
    speaker = int(os.environ.get("VOICEVOX_SPEAKER", "3"))
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
        make_card(text, i, len(segments), png, segment.get("scene", "clock"))
        seconds = duration(wav) + 0.45
        run("ffmpeg", "-y", "-loop", "1", "-framerate", "24", "-i", str(png),
            "-i", str(wav), "-filter_complex", "[1:a]apad[a]",
            "-map", "0:v", "-map", "[a]", "-t", f"{seconds:.3f}",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "27",
            "-pix_fmt", "yuv420p", "-r", "24", "-c:a", "aac",
            "-b:a", "128k", "-ar", "44100", str(mp4))
        clips.append(mp4)
    manifest = work / "concat.txt"
    manifest.write_text("".join(f"file '{clip.resolve()}'\n" for clip in clips), encoding="utf-8")
    final = out / "lateral-short.mp4"
    run("ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(manifest),
        "-c", "copy", "-movflags", "+faststart", str(final))
    print(f"Video ready: {final} ({duration(final):.1f} seconds)")


if __name__ == "__main__":
    main()
