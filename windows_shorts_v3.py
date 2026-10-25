#!/usr/bin/env python3
"""Lateral Shorts V3: voice-synced 30fps cinematic Fermi Shorts (Windows)."""
import os, math, json, wave, shutil, subprocess, tempfile
from pathlib import Path
from urllib.parse import quote
import cv2
import numpy as np
import requests
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps

HOME = Path.home()
ROOT = HOME / "Videos" / "lateral_shorts_assets"
ROOT.mkdir(parents=True, exist_ok=True)
OUTPUT = HOME / "lateral_shorts_v3.mp4"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
VOICE = os.getenv("VOICEVOX_URL", "http://127.0.0.1:50021").rstrip("/")
SPEAKER = int(os.getenv("VOICEVOX_SPEAKER", "8"))
W, H, FPS = 540, 960, 30
SCENES = [
    dict(shot="store", label="10年間の衝撃", big="219万円", sub="毎日1箱吸うと？",
         speech="毎日タバコを一箱。十年間で、およそ二百十九万円。"),
    dict(shot="wallet", label="計算の前提", big="1日 600円", sub="1日1箱・1箱600円と仮定",
         speech="まず、一箱六百円で計算します。"),
    dict(shot="calendar", label="30日分の費用", big="18,000円", sub="600円 × 30日",
         speech="三十日間なら、一万八千円。"),
    dict(shot="money", label="1年間の費用", big="219,000円", sub="600円 × 365日",
         speech="一年間なら、二十一万九千円です。"),
    dict(shot="money", label="10年で積み上がる額", big="2,190,000円", sub="600円 × 365日 × 10年",
         speech="そして十年間では、二百十九万円になります。"),
    dict(shot="travel", label="別の使い道なら？", big="219万円", sub="旅行・趣味・貯蓄などに",
         speech="同じお金を、旅行や趣味に使う選択もあります。あなたならどうしますか。"),
]
# Pexels provides motion footage through an optional personal API key.
SEARCHES = {
    "store": "convenience store cashier",
    "wallet": "counting money wallet close up",
    "calendar": "calendar turning pages",
    "money": "counting cash banknotes",
    "travel": "travel beautiful landscape",
}
# Public Unsplash photo IDs used ONLY as photographic fallback, not presented as video.
PHOTOS = {
    "store": "photo-1556742049-0cfed4f6a45d",
    "wallet": "photo-1554224155-6726b3ff858f",
    "calendar": "photo-1506784983877-45594efa4cbe",
    "money": "photo-1579621970563-ebec7560ff3e",
    "travel": "photo-1488646953014-85cb44e25828",
}

def font(size, bold=True):
    candidates = (["meiryob.ttc", "YuGothB.ttc", "meiryo.ttc"] if bold
                  else ["meiryo.ttc", "YuGothM.ttc"])
    for item in candidates:
        p = Path("C:/Windows/Fonts") / item
        if p.exists():
            return ImageFont.truetype(str(p), size)
    raise RuntimeError("Japanese font not found. Install Meiryo or Yu Gothic.")

def voice_file(text, path):
    q = requests.post(VOICE + "/audio_query",
                      params={"text": text, "speaker": SPEAKER}, timeout=45)
    q.raise_for_status()
    data = q.json()
    data["speedScale"] = 1.07
    # Do not accelerate whole audio to artificially fit the target.
    a = requests.post(VOICE + "/synthesis",
                      params={"speaker": SPEAKER}, json=data, timeout=90)
    a.raise_for_status()
    path.write_bytes(a.content)
    with wave.open(str(path), "rb") as f:
        return f.getnframes() / f.getframerate()


def get_pixabay(shot):
    """Optional Pixabay video, using a key from the local PC only."""
    key = os.getenv("PIXABAY_API_KEY", "").strip()
    if not key:
        return None
    dest = ROOT / (shot + "_pixabay.mp4")
    if dest.exists() and dest.stat().st_size > 100000:
        return dest
    # Search metadata is cached for at least 24 hours per Pixabay API policy.
    from datetime import datetime, timezone
    cache = ROOT / (shot + "_pixabay_search.json")
    try:
        payload = None
        if cache.exists() and (datetime.now(timezone.utc).timestamp() - cache.stat().st_mtime) < 86400:
            payload = json.loads(cache.read_text(encoding="utf-8"))
        if payload is None:
            response = requests.get(
                "https://pixabay.com/api/videos/",
                params={
                    "key": key,
                    "q": SEARCHES[shot],
                    "video_type": "film",
                    "safesearch": "true",
                    "per_page": 5,
                },
                timeout=25,
            )
            response.raise_for_status()
            payload = response.json()
            cache.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        candidates = []
        for hit in payload.get("hits", []):
            renditions = hit.get("videos", {})
            item = renditions.get("medium") or renditions.get("small") or {}
            if not item.get("url"):
                continue
            w, h = item.get("width", 0), item.get("height", 0)
            # Favour vertical media but crop landscape clips when necessary.
            score = (2 if h > w else 0) + (1 if min(w, h) >= 540 else 0)
            candidates.append((score, hit, item))
        if not candidates:
            print("No Pixabay footage for:", shot)
            return None
        _, chosen, item = sorted(candidates, key=lambda e: e[0], reverse=True)[0]
        with requests.get(item["url"], stream=True, timeout=60) as download:
            download.raise_for_status()
            with dest.open("wb") as output:
                total = 0
                for block in download.iter_content(128 * 1024):
                    if block:
                        total += len(block)
                        if total > 120 * 1024 * 1024:
                            raise RuntimeError("Pixabay download exceeds 120 MB")
                        output.write(block)
        print("Downloaded Pixabay footage:", shot, "source:", chosen.get("pageURL", ""))
        return dest
    except Exception as exc:
        dest.unlink(missing_ok=True)
        print("Pixabay unavailable:", shot, exc)
        return None

def get_pexels(shot):
    key = os.getenv("PEXELS_API_KEY", "").strip()
    if not key:
        return None
    dest = ROOT / (shot + ".mp4")
    if dest.exists() and dest.stat().st_size > 100000:
        return dest
    try:
        r = requests.get("https://api.pexels.com/v1/videos/search",
                         params={"query": SEARCHES[shot], "per_page": 8, "orientation": "portrait"},
                         headers={"Authorization": key}, timeout=25)
        r.raise_for_status()
        results = r.json().get("videos", [])
        candidates = []
        for video in results:
            for f in video.get("video_files", []):
                if f.get("link") and f.get("width", 0) >= 540 and f.get("height", 0) > f.get("width", 0):
                    candidates.append((f.get("width", 0), f["link"]))
        if not candidates:
            print("No portrait video found for", shot)
            return None
        url = sorted(candidates, key=lambda x: x[0])[0][1]
        with requests.get(url, stream=True, timeout=50) as response:
            response.raise_for_status()
            with dest.open("wb") as file:
                for block in response.iter_content(128*1024):
                    file.write(block)
        print("Downloaded Pexels footage:", shot)
        return dest
    except Exception as exc:
        print("Pexels unavailable:", shot, exc)
        return None

def photo_fallback(shot):
    dest = ROOT / (shot + ".jpg")
    if dest.exists():
        try:
            return Image.open(dest).convert("RGB")
        except Exception:
            dest.unlink()
    url = "https://images.unsplash.com/" + PHOTOS[shot] + "?w=1000&q=82"
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        dest.write_bytes(r.content)
        return Image.open(dest).convert("RGB")
    except Exception as exc:
        print("Photo fallback unavailable:", shot, exc)
        return None

def fit_image(im, progress):
    # Gentle Ken Burns zoom; photo itself does not become AI video.
    im = ImageOps.fit(im, (W+110, H+180))
    z = 1.0 + .065 * progress
    crop_w = int(W / z)
    crop_h = int(H / z)
    center_x = im.width // 2 + int(14*(progress-.5))
    center_y = im.height // 2 + int(20*(progress-.5))
    left = max(0, min(im.width-crop_w, center_x-crop_w//2))
    top = max(0, min(im.height-crop_h, center_y-crop_h//2))
    return im.crop((left, top, left+crop_w, top+crop_h)).resize((W,H), Image.Resampling.BILINEAR)

def safe_lines(draw, text, f, max_width=465):
    lines, cur = [], ""
    for ch in text:
        candidate = cur + ch
        if cur and draw.textbbox((0,0), candidate, font=f)[2] > max_width:
            lines.append(cur)
            cur = ch
        else:
            cur = candidate
    if cur:
        lines.append(cur)
    return lines

def paint(back, sc, t, duration, idx, actual_voice):
    im = Image.fromarray(cv2.cvtColor(back, cv2.COLOR_BGR2RGB)).convert("RGBA")
    # Darken the footage behind graphics but keep the scene visible.
    tint = Image.new("RGBA", (W,H), (5,12,22,120))
    im = Image.alpha_composite(im, tint)
    layer = Image.new("RGBA", (W,H), (0,0,0,0))
    d = ImageDraw.Draw(layer)
    gold = (255,205,72,255)
    white = (250,250,252,255)
    d.rounded_rectangle((27,65,513,73), radius=4, fill=gold)
    d.text((30,100), "ラテラルシンキング", font=font(28), fill=gold)
    d.rounded_rectangle((25,200,515,550), radius=27, fill=(5,13,29,185))
    d.text((40,237), sc["label"], font=font(29), fill=(225,235,245,255))
    size=61
    while size>32 and d.textbbox((0,0),sc["big"],font=font(size))[2]>466:
        size-=2
    # Make numerals grow at scene start (frame-by-frame, not a slideshow).
    grow = .91+.09*min(1.0, t/.38)
    ff = font(round(size*grow))
    width=d.textbbox((0,0),sc["big"],font=ff)[2]
    d.text(((W-width)//2,345),sc["big"],font=ff,fill=gold,stroke_width=2,stroke_fill=(0,0,0,255))
    sf=font(25)
    sublines=safe_lines(d,sc["sub"],sf)
    for k,line in enumerate(sublines):
        d.text((42,456+k*38),line,font=sf,fill=white)
    # Speech text appears while spoken; visual hierarchy still prioritizes numbers.
    if t < actual_voice+.2:
        d.rounded_rectangle((25,676,515,800),radius=22,fill=(5,13,29,210))
        subtitle_f=font(27)
        lines=safe_lines(d,sc["speech"],subtitle_f)
        for k,line in enumerate(lines[:3]):
            d.text((40,696+k*33),line,font=subtitle_f,fill=white)
    d.text((30,844),f"{idx+1:02d} / {len(SCENES):02d}",font=font(20),fill=gold)
    d.text((286,844),"VOICEVOX:春日部つむぎ",font=font(17),fill=white)
    d.rounded_rectangle((30,905,510,915),radius=4,fill=(75,89,111,255))
    d.rounded_rectangle((30,905,30+int(480*min(1,t/duration)),915),radius=4,fill=gold)
    im = Image.alpha_composite(im,layer).convert("RGB")
    return cv2.cvtColor(np.asarray(im),cv2.COLOR_RGB2BGR)

def render_scene(ffmpeg, sc, idx, duration, voice_sec, voice_path, work):
    shot=sc["shot"]
    user_clips = sorted((ROOT / shot).glob("*.mp4")) if (ROOT / shot).is_dir() else []
    direct = ROOT / (shot+".mp4")
    footage = (user_clips[0] if user_clips else
               direct if direct.exists() else (get_pixabay(shot) or get_pexels(shot)))
    cap = cv2.VideoCapture(str(footage)) if footage else None
    photo = None if cap and cap.isOpened() else photo_fallback(shot)
    mode = "REAL VIDEO" if cap and cap.isOpened() else "PHOTO MOTION" if photo else "ANIMATED GRADIENT"
    print(f"  scene {idx+1}: {mode}, {duration:.2f}s")
    out=work/f"{idx:02d}.mp4"
    args=[ffmpeg,"-hide_banner","-loglevel","error","-y",
          "-f","rawvideo","-vcodec","rawvideo","-pix_fmt","bgr24",
          "-s",f"{W}x{H}","-r",str(FPS),"-i","-",
          "-i",str(voice_path),"-filter_complex",
          "[0:v]scale=1080:1920:flags=lanczos,format=yuv420p[v];[1:a]apad[a]",
          "-map","[v]","-map","[a]","-t",f"{duration:.3f}",
          "-c:v","libx264","-preset","veryfast","-crf","20",
          "-r",str(FPS),"-c:a","aac","-b:a","128k",str(out)]
    proc = subprocess.Popen(args, stdin=subprocess.PIPE)
    count=round(duration*FPS)
    try:
        for n in range(count):
            t=n/FPS
            if cap and cap.isOpened():
                success,bg=cap.read()
                if not success:
                    cap.set(cv2.CAP_PROP_POS_FRAMES,0)
                    success,bg=cap.read()
                if success:
                    bg=cv2.resize(bg,(W,H),interpolation=cv2.INTER_LINEAR)
                else:
                    cap.release()
                    cap=None
                    photo=photo_fallback(shot)
            if not cap:
                if photo:
                    bg=cv2.cvtColor(np.asarray(fit_image(photo,t/duration)),cv2.COLOR_RGB2BGR)
                else:
                    bg=np.zeros((H,W,3),dtype=np.uint8)
                    k=t/duration
                    bg[:,:,0]=np.clip(55+10*math.sin(k*6),0,255)
                    bg[:,:,1]=np.linspace(35,70,H,dtype=np.uint8)[:,None]
                    bg[:,:,2]=np.linspace(18,48,H,dtype=np.uint8)[:,None]
            frame=paint(bg,sc,t,duration,idx,voice_sec)
            proc.stdin.write(frame.tobytes())
    except Exception:
        proc.kill()
        raise
    finally:
        if cap:
            cap.release()
        try:
            proc.stdin.close()
        except Exception:
            pass
    if proc.wait()!=0:
        raise RuntimeError("FFmpeg failed on scene "+str(idx+1))
    return out

def main():
    try:
        r=requests.get(VOICE+"/version",timeout=4)
        r.raise_for_status()
        print("VOICEVOX connected:",r.text)
    except requests.RequestException as e:
        raise SystemExit("VOICEVOX is not running. Launch the VOICEVOX app first.") from e
    with tempfile.TemporaryDirectory() as td:
        work=Path(td)
        lengths=[]
        audios=[]
        for i,sc in enumerate(SCENES):
            wav=work/f"voice_{i:02d}.wav"
            length=voice_file(sc["speech"],wav)
            lengths.append(length)
            audios.append(wav)
        base=[x+.28 for x in lengths]
        if sum(base)<=30:
            extra=(30-sum(base))/len(base)
            durations=[v+extra for v in base]
        else:
            durations=base
            print(f"Natural reading takes {sum(durations):.1f}s; preserving clear speech rather than accelerating.")
        print("Creating",round(sum(durations)*FPS),"animated frames...")
        clips=[render_scene(FFMPEG,s,i,durations[i],lengths[i],audios[i],work)
               for i,s in enumerate(SCENES)]
        manifest=work/"concat.txt"
        manifest.write_text("".join(f"file '{p.name}'\n" for p in clips),encoding="utf-8")
        subprocess.run([FFMPEG,"-hide_banner","-loglevel","error","-y",
                        "-f","concat","-safe","0","-i",str(manifest),
                        "-c","copy","-movflags","+faststart",str(OUTPUT)],
                       cwd=str(work),check=True)
    print("SUCCESS:",OUTPUT)
    print("Review the result before publishing. Footage: own media or Pexels optional; otherwise animated photos.")
if __name__=="__main__":
    main()
