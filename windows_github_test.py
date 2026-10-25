# Windows local test: GitHub -> Python -> MP4 (VOICEVOX optional)
from pathlib import Path
import subprocess
import tempfile
import urllib.parse
import requests
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

OUT = Path.home() / "Desktop"
if not OUT.is_dir():
    OUT = Path.home()
OUT = OUT / "lateral_github_test.mp4"

def font(size):
    for name in ["C:/Windows/Fonts/meiryob.ttc", "C:/Windows/Fonts/meiryo.ttc", "C:/Windows/Fonts/YuGothB.ttc"]:
        if Path(name).exists():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default()

def main():
    print("Checking FFmpeg...")
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    print("FFmpeg:", ffmpeg)
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        png = tmp / "frame.png"
        wav = tmp / "voice.wav"
        img = Image.new("RGB", (540, 960), (12, 25, 42))
        draw = ImageDraw.Draw(img)
        draw.rectangle((30, 90, 510, 105), fill=(255, 205, 67))
        draw.text((40, 145), "ラテラルシンキング", font=font(37), fill=(255, 205, 67))
        draw.text((40, 345), "GitHub連携", font=font(61), fill="white")
        draw.text((40, 445), "動画生成テスト成功！", font=font(31), fill="white")
        draw.text((40, 800), "Windows × Python × FFmpeg", font=font(23), fill=(170, 195, 212))
        img.save(png)

        # When VOICEVOX Engine is running, add narration automatically.
        has_voice = False
        base = "http://127.0.0.1:50021"
        try:
            requests.get(base + "/version", timeout=2).raise_for_status()
            text = "GitHubとパイソンの連携テスト、成功です！"
            query = requests.post(base + "/audio_query", params={"text": text, "speaker": 8}, timeout=15)
            query.raise_for_status()
            result = requests.post(base + "/synthesis", params={"speaker": 8}, json=query.json(), timeout=30)
            result.raise_for_status()
            wav.write_bytes(result.content)
            has_voice = True
        except requests.RequestException:
            print("VOICEVOX not running; making a silent video (this is OK).")

        cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-loop", "1", "-framerate", "24", "-i", str(png)]
        if has_voice:
            cmd += ["-i", str(wav), "-af", "apad", "-c:a", "aac", "-b:a", "128k"]
        cmd += ["-t", "5", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(OUT)]
        subprocess.run(cmd, check=True)
    print("SUCCESS:", OUT)

if __name__ == "__main__":
    main()
