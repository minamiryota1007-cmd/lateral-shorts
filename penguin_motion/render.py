"""Render the penguin short. VOICEVOX must be running unless --no-voice is selected."""
import argparse, json, os, subprocess, tempfile, time, urllib.parse, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SCENES=[(4,'皇帝ペンギン３号を、現実で打ったら？'),(4,'氷の上を時速１０キロで滑ると仮定。'),(5,'２０メートル先のゴールまで、７.２秒！'),(4,'時速１００キロのシュートなら、０.７２秒！'),(4,'到着まで１０倍！ キーパー、まだ来ない？'),(4,'しかも、サッカー場は芝生。滑らん！'),(5,'必殺技というより、ペンギンの大移動！')]
def run(*args): subprocess.run(list(args),check=True)
def request(url,data=None):
 with urllib.request.urlopen(urllib.request.Request(url,data=data,headers={'Content-Type':'application/json'} if data else {}),timeout=120) as r:return r.read()
def speak(text, speaker, out):
 base=os.getenv('VOICEVOX_URL','http://127.0.0.1:50021').rstrip('/')
 query=urllib.parse.urlencode({'text':text,'speaker':speaker})
 settings=json.loads(request(base+'/audio_query?'+query,b''));settings['speedScale']=1.2
 wav=request(base+'/synthesis?'+urllib.parse.urlencode({'speaker':speaker}),json.dumps(settings).encode())
 out.write_bytes(wav)
def main():
 p=argparse.ArgumentParser();p.add_argument('--no-voice',action='store_true');p.add_argument('--speaker',type=int,default=13);p.add_argument('--output',default='output/penguin_motion.mp4');a=p.parse_args()
 output=Path(a.output).resolve();output.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory() as temp:
  tmp=Path(temp); clips=[]
  for i,(duration,words) in enumerate(SCENES):
   video=tmp/f'v{i}.mp4'; audio=tmp/f'a{i}.wav'; clip=tmp/f'c{i}.mp4'; frames=duration*25
   # Gentle zoom and lateral tracking; this animates the camera, not animal anatomy.
   zoom="zoompan=z='min(zoom+0.0005,1.12)':x='(iw-iw/zoom)*(0.25+0.5*on/"+str(frames)+")':y='(ih-ih/zoom)/2':d=1:s=720x1280:fps=25"
   run('ffmpeg','-y','-loglevel','error','-loop','1','-framerate','25','-i',str(ROOT/'assets'/f'{i}.jpg'),'-vf',zoom,'-frames:v',str(frames),'-c:v','libx264','-preset','ultrafast','-crf','23','-pix_fmt','yuv420p',str(video))
   if a.no_voice:
    run('ffmpeg','-y','-loglevel','error','-f','lavfi','-i','anullsrc=r=24000:cl=mono','-t',str(duration),str(audio))
   else:
    speak(words,a.speaker,audio)
    # Refuse to truncate speech; raise a clear error when a line overruns its scene.
    duration_audio=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(audio)]))
    if duration_audio>duration-.1: raise RuntimeError(f'台詞 {i+1} が長すぎます: {duration_audio:.2f}秒 / {duration}秒')
   run('ffmpeg','-y','-loglevel','error','-i',str(video),'-i',str(audio),'-af',f'apad,atrim=duration={duration}', '-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-ar','24000','-ac','1','-t',str(duration),str(clip));clips.append(clip)
  listing=tmp/'concat.txt';listing.write_text(''.join(f"file '{x.as_posix()}'\n" for x in clips),encoding='utf-8')
  combined=tmp/'combined.mp4';run('ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',str(listing),'-c','copy',str(combined))
  run('ffmpeg','-y','-loglevel','error','-i',str(combined),'-stream_loop','-1','-i',str(ROOT/'assets'/'bgm.mp3'),'-filter_complex','[1:a]volume=0.17[m];[0:a][m]amix=inputs=2:duration=first:normalize=0[a]','-map','0:v','-map','[a]','-c:v','copy','-c:a','aac','-movflags','+faststart',str(output))
  print('完成:',output)
if __name__=='__main__':main()
