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


def lines_for(text, max_chars=13):
    lines = []
    for paragraph in text.split("\n"):
        while len(paragraph) > max_chars:
            lines.append(paragraph[:max_chars])
            paragraph = paragraph[max_chars:]
        lines.append(paragraph)
    return lines


def make_card(text, number, total, output):
    image = Image.new("RGB", (WIDTH, HEIGHT), (13, 26, 48))
    draw = ImageDraw.Draw(image)
    accent = (70, 220, 197)
    draw.rounded_rectangle((46, 85, 674, 105), radius=10, fill=accent)
    font = ImageFont.truetype(FONT, 57)
    small = ImageFont.truetype(FONT, 30)
    draw.text((54, 135), "ラテラルシンキング", font=small, fill=accent)
    lines = lines_for(text)
    spacing = 24
    boxes = [draw.textbbox((0, 0), line, font=font) for line in lines]
    heights = [b[3] - b[1] for b in boxes]
    total_height = sum(heights) + spacing * (len(lines) - 1)
    y = (HEIGHT - total_height) // 2
    for line, h in zip(lines, heights):
        box = draw.textbbox((0, 0), line, font=font)
        x = (WIDTH - (box[2] - box[0])) // 2
        draw.text((x, y), line, font=font, fill="white", stroke_width=1)
        y += h + spacing
    draw.text((54, 1160), f"{number:02d} / {total:02d}", font=small, fill=accent)
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
        make_card(text, i, len(segments), png)
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
