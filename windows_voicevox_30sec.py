#!/usr/bin/env python3
# Windows local test: VOICEVOX narration + 30-second vertical video.
# Install: pip install Pillow requests imageio-ffmpeg
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import wave
import os

import requests
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

WIDTH, HEIGHT, SCENE_SECONDS = 540, 960, 5
BASE = os.environ.get("VOICEVOX_URL", "http://127.0.0.1:50021").rstrip("/")
SPEAKER = int(os.environ.get("VOICEVOX_SPEAKER", "8"))
OUT_DIR = Path.home() / "Desktop"
if not OUT_DIR.exists():
    OUT_DIR = Path.home()
OUTPUT = OUT_DIR / "lateral_voicevox_30sec.mp4"

# Example uses an explicit 600-yen-per-pack assumption; prices vary.
SCENES = [
    ("1日1箱を10年間", "タバコを毎日一箱、十年間吸ったらどうなる？", "もしも計算"),
    ("1箱600円と仮定", "一箱六百円として、計算してみよう。", "前提条件"),
    ("1か月 約1万8千円", "三十日で一万八千円。", "30日で計算"),
    ("1年間 21万9千円", "一年では、二十一万九千円。", "365日で計算"),
    ("10年間 219万円", "十年間なら、なんと二百十九万円。", "365日×10年"),
    ("お金だけじゃない", "健康への影響も。あなたなら、このお金を何に使う？", "計算の先へ"),
]

def font(size):
    for p in (
        "C:/Windows/Fonts/meiryob.ttc",
        "C:/Windows/Fonts/meiryo.ttc",
        "C:/Windows/Fonts/YuGothB.ttc",
        "C:/Windows/Fonts/msgothic.ttc",
    ):
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    raise RuntimeError("Japanese font not found in C:/Windows/Fonts")

def center(draw, y, text, f, fill):
    bb = draw.textbbox((0, 0), text, font=f)
    x = (WIDTH - (bb[2] - bb[0])) // 2
    draw.text((x, y), text, font=f, fill=fill)

def image_for(headline, subtitle, tag, number, path):
    im = Image.new("RGB", (WIDTH, HEIGHT))
    px = im.load()
    for y in range(HEIGHT):
        t = y / HEIGHT
        color = (int(12 + 18*t), int(25 + 15*t), int(49 + 28*t))
        for x in range(WIDTH):
            px[x, y] = color
    d = ImageDraw.Draw(im)
    yellow = (255, 205, 72)
    d.rounded_rectangle((24, 65, 516, 75), radius=4, fill=yellow)
    center(d, 108, "ラテラルシンキング", font(30), yellow)
    center(d, 275, tag, font(31), (180, 207, 222))
    size = 54
    while size > 22 and d.textbbox((0, 0), headline, font=font(size))[2] > 492:
        size -= 2
    center(d, 384, headline, font(size), (255, 245, 223))
    d.rounded_rectangle((26, 625, 514, 790), radius=23, fill=(29, 49, 71))
    # Wrap Japanese text without external layout dependencies.
    text_font = font(30)
    lines, line = [], ""
    for ch in subtitle:
        if line and d.textbbox((0, 0), line+ch, font=text_font)[2] > 448:
            lines.append(line)
            line = ch
        else:
            line += ch
    if line:
        lines.append(line)
    for idx, text in enumerate(lines):
        center(d, 663 + idx*45, text, text_font, "white")
    d.text((28, 847), f"{number:02d} / 06", font=font(20), fill=yellow)
    d.text((260, 847), "VOICEVOX:春日部つむぎ", font=font(17), fill=(184, 199, 210))
    im.save(path)

def narration(text, wav_path):
    try:
        q = requests.post(BASE + "/audio_query", params={"text": text, "speaker": SPEAKER}, timeout=30)
        q.raise_for_status()
        payload = q.json()
        payload["speedScale"] = 1.55
        s = requests.post(BASE + "/synthesis", params={"speaker": SPEAKER}, json=payload, timeout=90)
        s.raise_for_status()
        wav_path.write_bytes(s.content)
    except requests.RequestException as exc:
        raise RuntimeError("VOICEVOX synthesis failed. Keep VOICEVOX running and verify http://127.0.0.1:50021/version") from exc
    with wave.open(str(wav_path), "rb") as w:
        length = w.getnframes() / w.getframerate()
    if length > SCENE_SECONDS:
        raise RuntimeError(f"Narration is too long ({length:.2f}s > 5s). Shorten the segment text or increase speedScale.")
    return length

def main():
    try:
        r = requests.get(BASE + "/version", timeout=4)
        r.raise_for_status()
        print("VOICEVOX connected:", r.text)
        speakers = requests.get(BASE + "/speakers", timeout=10)
        speakers.raise_for_status()
        available_ids = [s["id"] for sp in speakers.json() for s in sp.get("styles", [])]
        if SPEAKER not in available_ids:
            raise RuntimeError(f"VOICEVOX_SPEAKER {SPEAKER} is unavailable. Choose an id from {available_ids[:30]}.")
    except requests.RequestException as exc:
        raise RuntimeError("VOICEVOX is not running on port 50021. Install/open VOICEVOX and retry.") from exc
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    with TemporaryDirectory() as tmp:
        work = Path(tmp)
        clips = []
        for i, (headline, spoken, tag) in enumerate(SCENES, 1):
            png, wav, mp4 = (work / f"{i:02d}.{ext}" for ext in ("png", "wav", "mp4"))
            image_for(headline, spoken, tag, i, png)
            length = narration(spoken, wav)
            print(f"Scene {i}/6: {length:.2f}s voice")
            subprocess.run([
                ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
                "-loop", "1", "-framerate", "24", "-i", str(png),
                "-i", str(wav), "-af", "apad", "-t", str(SCENE_SECONDS),
                "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
                "-r", "24", "-c:a", "aac", "-ar", "44100", "-b:a", "128k",
                str(mp4),
            ], check=True)
            clips.append(mp4)
        manifest = work / "concat.txt"
        manifest.write_text("".join(f"file '{p.name}'\n" for p in clips), encoding="utf-8")
        subprocess.run([
            ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-f", "concat",
            "-safe", "0", "-i", str(manifest), "-c", "copy", "-movflags",
            "+faststart", str(OUTPUT),
        ], check=True, cwd=str(work))
    print("SUCCESS:", OUTPUT)
    print("30 seconds, 540x960. Confirm accuracy and audio before publishing.")

if __name__ == "__main__":
    main()
