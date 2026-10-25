"""Generate aligned VOICEVOX narration for Remotion V7 (Python 3.13)."""
import json
import os
import wave
from pathlib import Path
import requests

HERE=Path(__file__).resolve().parent
PUBLIC=HERE/"public"
PUBLIC.mkdir(exist_ok=True)
URL=os.getenv("VOICEVOX_URL","http://127.0.0.1:50021").rstrip("/")
FPS=30
SCENES=[
    (5,"通勤で待つ赤信号。人生では、何日分になるのでしょう。"),
    (5,"一日に通る信号は、往復で二十か所と仮定します。"),
    (5,"そのうち、四十一パーセントが赤信号だとしましょう。"),
    (5,"さらに、赤で止まる時間は、一回平均六十秒とします。"),
    (6,"すると一日の待ち時間は、約八点二分です。"),
    (6,"年間二百四十日、これを四十年間続けると。"),
    (7,"なんと人生の約五十五日間を、信号待ちに費やす計算です。"),
    (7,"あなたなら、その時間をどう考えますか。"),
]

def get_voice():
    info=requests.get(URL+"/speakers",timeout=10)
    info.raise_for_status()
    names=info.json()
    custom=os.getenv("VOICEVOX_SPEAKER","").strip()
    if custom:
        return int(custom)
    for person in names:
        if "青山龍星" in person["name"]:
            style=next((s for s in person["styles"] if s["name"]=="ノーマル"),person["styles"][0])
            print("VOICEVOX:",person["name"],"style",style["id"])
            return int(style["id"])
    raise RuntimeError("VOICEVOXに青山龍星が見つかりません。音声ライブラリを確認してください。")

def synth(text,speaker):
    r=requests.post(URL+"/audio_query",params={"text":text,"speaker":speaker},timeout=30)
    r.raise_for_status()
    query=r.json()
    query["speedScale"]=1.05
    query["pitchScale"]=-0.03
    query["intonationScale"]=0.98
    r=requests.post(URL+"/synthesis",params={"speaker":speaker},json=query,timeout=60)
    r.raise_for_status()
    return r.content

def main():
    try:
        requests.get(URL+"/version",timeout=5).raise_for_status()
    except requests.RequestException as exc:
        raise SystemExit("VOICEVOXを先に起動してください。") from exc
    speaker=get_voice()
    import io
    all_audio=None
    audio_spec=None
    for seconds,text in SCENES:
        audio=synth(text,speaker)
        with wave.open(io.BytesIO(audio),"rb") as w:
            specs=(w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getcomptype())
            pcm=w.readframes(w.getnframes())
        if specs[3]!="NONE":
            raise RuntimeError("PCM WAV expected")
        if audio_spec is None:
            audio_spec=specs
            sr=specs[2]
            all_audio=bytearray(b"\0"*(sum(s for s,_ in SCENES)*sr*specs[0]*specs[1]))
        if specs!=audio_spec:
            raise RuntimeError("VOICEVOX output format changed unexpectedly")
        assert all_audio is not None
        allotted=int(seconds*sr)
        frame_bytes=specs[0]*specs[1]
        spoken=len(pcm)//frame_bytes
        if spoken>allotted-int(sr*.25):
            print("Note: scene narration exceeded slot, trimming:",text)
            pcm=pcm[:(allotted-int(sr*.25))*frame_bytes]
        index=sum(x for x,_ in SCENES[:SCENES.index((seconds,text))])
        offset=int((index+.20)*sr)*frame_bytes
        all_audio[offset:offset+len(pcm)]=pcm
    out=PUBLIC/"narration.wav"
    assert audio_spec is not None and all_audio is not None
    with wave.open(str(out),"wb") as w:
        w.setnchannels(audio_spec[0])
        w.setsampwidth(audio_spec[1])
        w.setframerate(audio_spec[2])
        w.writeframes(all_audio)
    (HERE/"render-props.json").write_text(json.dumps({"withAudio":True}),encoding="utf-8")
    print("Narration generated:",out)

if __name__=="__main__":
    main()
