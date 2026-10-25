"""Prepare 45s VOICEVOX narration and optional Pixabay B-roll for V8."""
import io
import json
import os
import subprocess
import wave
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parent
PUBLIC=ROOT/"public"
ASSETS=PUBLIC/"assets"
PUBLIC.mkdir(parents=True,exist_ok=True)
ASSETS.mkdir(parents=True,exist_ok=True)
ENGINE=os.getenv("VOICEVOX_URL","http://127.0.0.1:50021").rstrip("/")
SCENES=[
    (7,"次元のマグナム弾を、素手でキャッチできるのか。普通に撃たれたら、まず不可能。"),
    (9,"弾丸を約十点二グラム、初速を秒速三百三十メートルとすると。エネルギーは、約五百五十五ジュール。"),
    (9,"では、真上に撃ったら。重力と空気抵抗によって、上昇するほど減速します。"),
    (10,"簡易モデルでは、最高高度は約五百から千百メートル。最高点では、鉛直方向の速度がゼロ。"),
    (10,"でも、止まるのは一瞬。弾丸は回転し、やがて落下します。安全にキャッチできるわけではありません。"),
]
QUERIES=["revolver gun cinematic close up","bullet macro flying slow motion","blue sky clouds","high altitude clouds sky","clouds sky blue"]
NAMES=["revolver.mp4","bullet.mp4","sky.mp4","clouds.mp4","apex.mp4"]
def get_speaker():
    answer=requests.get(ENGINE+"/speakers",timeout=10)
    answer.raise_for_status()
    speakers=answer.json()
    manual=os.getenv("VOICEVOX_SPEAKER","").strip()
    if manual:
        return int(manual)
    for speaker in speakers:
        if "青山龍星" in speaker["name"]:
            styles=speaker["styles"]
            normal=next((a for a in styles if a["name"]=="ノーマル"),styles[0])
            print("Voice:",speaker["name"],"speaker ID",normal["id"])
            return int(normal["id"])
    raise RuntimeError("VOICEVOX 青山龍星が見つかりません。")
def generate_voice():
    r=requests.get(ENGINE+"/version",timeout=6)
    r.raise_for_status()
    speaker=get_speaker()
    combined=None
    format_info=None
    cursor=0
    for i,(slot,text) in enumerate(SCENES):
        q=requests.post(ENGINE+"/audio_query",params={"text":text,"speaker":speaker},timeout=30)
        q.raise_for_status()
        params=q.json()
        params["speedScale"]=1.06
        params["pitchScale"]=-.035
        params["intonationScale"]=.96
        r=requests.post(ENGINE+"/synthesis",params={"speaker":speaker},json=params,timeout=90)
        r.raise_for_status()
        with wave.open(io.BytesIO(r.content),"rb") as audio:
            fmt=(audio.getnchannels(),audio.getsampwidth(),audio.getframerate())
            pcm=audio.readframes(audio.getnframes())
        if format_info is None:
            format_info=fmt
            combined=bytearray(b"\x00"*int(sum(x[0] for x in SCENES)*fmt[2]*fmt[0]*fmt[1]))
        if fmt!=format_info:
            raise RuntimeError("VOICEVOX changed audio format")
        seconds=len(pcm)/fmt[2]/fmt[0]/fmt[1]
        if seconds>slot-.3:
            raise RuntimeError(f"Scene {i+1} speech ({seconds:.2f}s) exceeds slot ({slot}s). Shorten its narration; do not cut speech.")
        assert combined is not None
        offset=int((cursor+.12)*fmt[2])*fmt[0]*fmt[1]
        combined[offset:offset+len(pcm)]=pcm
        cursor+=slot
        print(f"Scene {i+1}: voice {seconds:.2f}s / slot {slot}s")
    assert combined is not None and format_info is not None
    with wave.open(str(PUBLIC/"narration.wav"),"wb") as out:
        out.setnchannels(format_info[0])
        out.setsampwidth(format_info[1])
        out.setframerate(format_info[2])
        out.writeframes(combined)
    print("VOICEVOX audio prepared.")
def get_pixabay():
    key=os.getenv("PIXABAY_API_KEY","").strip()
    if not key:
        print("No PIXABAY_API_KEY. Procedural motion background will be used.")
        return []
    try:
        import imageio_ffmpeg
        ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        print("Install imageio-ffmpeg for stock footage trimming. Skipping media.")
        return []
    from datetime import datetime,timezone
    cached_assets=[]
    for idx,(name,search) in enumerate(zip(NAMES,QUERIES)):
        output=ASSETS/name
        if output.exists() and output.stat().st_size>100000:
            cached_assets.append(name)
            continue
        cache=ROOT/f"pixabay_search_{idx}.json"
        try:
            payload=None
            if cache.exists() and datetime.now(timezone.utc).timestamp()-cache.stat().st_mtime<86400:
                payload=json.loads(cache.read_text(encoding="utf-8"))
            if payload is None:
                response=requests.get("https://pixabay.com/api/videos/",
                    params={"key":key,"q":search,"safesearch":"true","video_type":"film","per_page":5},timeout=25)
                if response.status_code!=200:
                    print("Pixabay scene",idx+1,"HTTP",response.status_code,response.text[:150].replace(key,"[REDACTED]"))
                    cached_assets.append("")
                    continue
                payload=response.json()
                cache.write_text(json.dumps(payload),encoding="utf-8")
            candidates=[]
            for hit in payload.get("hits",[]):
                mp4=hit.get("videos",{}).get("medium") or hit.get("videos",{}).get("small") or {}
                if mp4.get("url"):
                    w,h=mp4.get("width",0),mp4.get("height",0)
                    candidates.append((int(h>w),w*h,mp4["url"]))
            if not candidates:
                print("Pixabay: no video for scene",idx+1)
                cached_assets.append("")
                continue
            url=sorted(candidates,reverse=True)[0][2]
            original=ASSETS/(name+".download.mp4")
            with requests.get(url,stream=True,timeout=70) as response:
                response.raise_for_status()
                size=0
                with original.open("wb") as out:
                    for block in response.iter_content(128*1024):
                        size+=len(block)
                        if size>90*1024*1024:
                            raise RuntimeError("Stock clip exceeds 90MB")
                        out.write(block)
            duration=SCENES[idx][0]
            cmd=[ffmpeg,"-hide_banner","-loglevel","error","-y","-stream_loop","-1","-i",str(original),
                 "-t",str(duration+.5),"-vf","scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
                 "-an","-c:v","libx264","-preset","ultrafast","-crf","25","-pix_fmt","yuv420p",str(output)]
            subprocess.run(cmd,check=True)
            original.unlink(missing_ok=True)
            cached_assets.append(name)
            print("B-roll downloaded and conformed:",name)
        except Exception as exc:
            (ASSETS/(name+".download.mp4")).unlink(missing_ok=True)
            output.unlink(missing_ok=True)
            print("Stock footage unavailable for scene",idx+1,str(exc).replace(key,"[REDACTED]")[:240])
            cached_assets.append("")
    return cached_assets
def main():
    # Audio always synthesized before optional footage to fail early if VOICEVOX is unavailable.
    generate_voice()
    assets=get_pixabay()
    (ROOT/"render-props.json").write_text(json.dumps({"withAudio":True,"assets":assets},ensure_ascii=False),encoding="utf-8")
    print("Render settings prepared.")
if __name__=="__main__":
    main()
