"""Build 7-scene VOICEVOX narration, subtle background music, and optional real stock backgrounds."""
import io, math, json, os, struct, subprocess, wave
from pathlib import Path
from datetime import datetime, timezone
import requests

BASE=Path(__file__).resolve().parent
PUB=BASE/"public"
ASSETS=PUB/"assets"
ASSETS.mkdir(parents=True,exist_ok=True)
VOICE=os.getenv("VOICEVOX_URL","http://127.0.0.1:50021").rstrip("/")
# Segment lengths must total exactly 45 seconds and match Remotion.
SCENES=[
 (6,"次元のマグナム弾を手でキャッチ？ 結論、普通に撃たれたら絶対無理！"),
 (6,"初速は秒速三百三十メートル。エネルギーは、約五百五十五ジュール！"),
 (5,"これ、約四点七キロのボウリング球を十二メートル持ち上げた分！"),
 (8,"じゃあ真上なら？ 重力と空気抵抗で、弾丸の上昇速度がぐんぐん落ちる！"),
 (9,"計算すると、最高高度は約八百八十八メートル！ 頂点まで約十点五秒！"),
 (6,"ただし、空気抵抗の仮定で高さは大きく変わります！"),
 (5,"一瞬速度ゼロ。でも安全にキャッチなんて、できません！"),
]
QUERIES=[
 "revolver handgun close up cinematic",
 "bullet ammunition macro photography",
 "bowling ball bowling alley",
 "blue sky clouds moving",
 "high altitude blue sky clouds",
 "clouds aerial flying dramatic",
 "dark sky clouds cinematic",
]
NAMES=["revolver.mp4","bullet.mp4","bowling.mp4","sky.mp4","altitude.mp4","range.mp4","ending.mp4"]

def get_speaker():
    response=requests.get(VOICE+"/speakers",timeout=15)
    response.raise_for_status()
    requested=os.getenv("VOICEVOX_SPEAKER","").strip()
    entries=response.json()
    if requested:
        for person in entries:
            if any(int(style["id"])==int(requested) for style in person["styles"]):
                print("Voice:",person["name"],requested)
                return int(requested)
        raise RuntimeError("指定したVOICEVOX_SPEAKERが見つかりません。")
    for person in entries:
        if "青山龍星" in person["name"]:
            selected=next((style for style in person["styles"] if "テンション" in style["name"] or "熱血" in style["name"]),None)
            selected=selected or next((style for style in person["styles"] if style["name"]=="ノーマル"),person["styles"][0])
            print("Voice:",person["name"],selected["name"],selected["id"])
            return int(selected["id"])
    raise RuntimeError("VOICEVOX青山龍星が見つかりません。")

def make_audio():
    requests.get(VOICE+"/version",timeout=5).raise_for_status()
    speaker=get_speaker()
    combined=None
    spec=None
    elapsed=0
    for i,(seconds,words) in enumerate(SCENES):
        q=requests.post(VOICE+"/audio_query",params={"speaker":speaker,"text":words},timeout=30)
        q.raise_for_status()
        req=q.json()
        req["speedScale"]=1.12
        req["pitchScale"]=-0.01
        req["intonationScale"]=1.16
        reply=requests.post(VOICE+"/synthesis",params={"speaker":speaker},json=req,timeout=90)
        reply.raise_for_status()
        with wave.open(io.BytesIO(reply.content),"rb") as wav:
            info=(wav.getnchannels(),wav.getsampwidth(),wav.getframerate())
            pcm=wav.readframes(wav.getnframes())
        if spec is None:
            spec=info
            combined=bytearray(sum(s for s,_ in SCENES)*info[2]*info[0]*info[1])
        if info!=spec:
            raise RuntimeError("VOICEVOXの音声形式が途中で変わりました。")
        speech_sec=len(pcm)/(info[0]*info[1]*info[2])
        if speech_sec>seconds-.20:
            print(f"Voice too long: scene {i+1}: {speech_sec:.2f}s > {seconds-.2:.2f}s.")
            print("Text:",words)
            raise RuntimeError("台詞が長いため中断。音声はカットしません。")
        assert combined is not None
        offset=round((elapsed+.07)*info[2])*info[0]*info[1]
        combined[offset:offset+len(pcm)]=pcm
        elapsed+=seconds
        print("Voice scene",i+1,round(speech_sec,2),"sec")
    assert spec and combined is not None
    with wave.open(str(PUB/"narration.wav"),"wb") as out:
        out.setnchannels(spec[0]);out.setsampwidth(spec[1]);out.setframerate(spec[2]);out.writeframes(combined)

def make_music():
    """Subtle generated synth pulse; Remotion mutes it briefly at the apex."""
    path=PUB/"bgm.wav"
    if path.exists() and path.stat().st_size>300000:
        return
    sr=16000
    with wave.open(str(path),"wb") as out:
        out.setnchannels(1);out.setsampwidth(2);out.setframerate(sr)
        # 4-second loop, independent of narrator, avoids copyrighted music.
        for i in range(4*sr):
            t=i/sr
            beat=(t*2)%1
            pulse=math.exp(-9*beat)
            sound=.17*math.sin(2*math.pi*55*t)*pulse
            sound+=.09*math.sin(2*math.pi*110*t)*(.40+.60*pulse)
            fade=min(1,i/(sr*.12),(4*sr-i)/(sr*.12))
            out.writeframesraw(struct.pack("<h",int(max(-1,min(1,sound*max(0,fade)))*32767)))

def stock_assets():
    key=os.getenv("PIXABAY_API_KEY","").strip()
    paths=[]
    if not key:
        print("Pixabay API key not set; rendered VFX will be used.")
    try:
        import imageio_ffmpeg
        ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        print("No imageio-ffmpeg; stock clips disabled.")
        return [""]*len(SCENES)
    for i,(term,name) in enumerate(zip(QUERIES,NAMES)):
        dest=ASSETS/name
        if dest.exists() and dest.stat().st_size>100000:
            paths.append(name)
            continue
        if not key:
            paths.append("")
            continue
        metadata=BASE/f"pixabay_cache_{i}.json"
        try:
            if metadata.exists() and datetime.now(timezone.utc).timestamp()-metadata.stat().st_mtime <86400:
                data=json.loads(metadata.read_text(encoding="utf-8"))
            else:
                response=requests.get("https://pixabay.com/api/videos/",
                    params={"key":key,"q":term,"per_page":5,"safesearch":"true","video_type":"film"},timeout=30)
                if response.status_code!=200:
                    print(f"Pixabay search {i+1}: HTTP",response.status_code,response.text[:130].replace(key,"[REDACTED]"))
                    paths.append("")
                    continue
                data=response.json()
                metadata.write_text(json.dumps(data),encoding="utf-8")
            picks=[]
            for h in data.get("hits",[]):
                v=h.get("videos",{})
                candidate=v.get("medium") or v.get("small") or {}
                if candidate.get("url"):
                    w,ht=candidate.get("width",0),candidate.get("height",0)
                    picks.append((int(ht>w),w*ht,candidate["url"]))
            if not picks:
                paths.append("")
                continue
            selected=sorted(picks,reverse=True)[0][2]
            temp=ASSETS/(name+".partial.mp4")
            total=0
            with requests.get(selected,stream=True,timeout=75) as r:
                r.raise_for_status()
                with temp.open("wb") as f:
                    for block in r.iter_content(131072):
                        total+=len(block)
                        if total>90*1024*1024:
                            raise RuntimeError("Stock footage too large")
                        f.write(block)
            command=[ffmpeg,"-hide_banner","-loglevel","error","-y","-stream_loop","-1","-i",str(temp),
                "-t",str(SCENES[i][0]+.5),"-vf","scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
                "-an","-c:v","libx264","-preset","veryfast","-crf","22","-pix_fmt","yuv420p",str(dest)]
            subprocess.run(command,check=True)
            temp.unlink(missing_ok=True)
            paths.append(name)
            print("Stock scene",i+1,"ready",name)
        except Exception as exc:
            dest.unlink(missing_ok=True)
            (ASSETS/(name+".partial.mp4")).unlink(missing_ok=True)
            print("Stock scene",i+1,"failed:",str(exc).replace(key,"[REDACTED]")[:180])
            paths.append("")
    return paths

def main():
    make_audio()
    make_music()
    assets=stock_assets()
    (BASE/"render-props.json").write_text(json.dumps({"withAudio":True,"assets":assets},ensure_ascii=False),encoding="utf-8")
    print("All media prepared.")

if __name__=="__main__":
    main()
