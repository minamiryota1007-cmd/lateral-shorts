import React from 'react';
import {AbsoluteFill,Audio,OffthreadVideo,interpolate,spring,staticFile,useCurrentFrame,useVideoConfig} from 'remotion';
import physics from './physics.json';

type Props={withAudio?:boolean;assets?:string[];};
const Y='#FFE05E',R='#FF5167',W='#FFFFFF',M='#BACBDC';
const chapters=[
 {start:0,end:6,title:'次元のマグナム弾',big:'素手でキャッチ!?' ,caption:'結論：水平に撃たれたら、まず不可能！',kind:'revolver'},
 {start:6,end:12,title:'10.2g × 330m/s',big:'約555J',caption:'E = ½ × 0.0102 × 330²',kind:'bullet'},
 {start:12,end:17,title:'衝撃の比較！',big:'ボウリング球 × 12m',caption:'約4.7kgの球を12mの高さに置く位置エネルギー相当',kind:'bowling'},
 {start:17,end:25,title:'もし真上だったら？',big:'重力 ＋ 空気抵抗',caption:'弾丸は上昇するほど減速！',kind:'sky'},
 {start:25,end:34,title:'鉛直速度ゼロの瞬間',big:'約888m！',caption:'基準Cd=0.45｜約10.54秒で頂点',kind:'altitude'},
 {start:34,end:40,title:'抗力の違いを比較',big:'約496〜1,171m',caption:'条件を変えた感度分析。実射の予測値ではない',kind:'comparison'},
 {start:40,end:45,title:'科学の結論',big:'止まっても危険！',caption:'鉛直速度0でも、安全にキャッチはできない',kind:'ending'},
] as const;
const TOTAL=1350;
const clamp=(n:number,a=0,b=1)=>Math.max(a,Math.min(b,n));
const ease=(n:number)=>1-Math.pow(1-clamp(n),3);
const data=physics as {initialEnergyJ:number;bowlingComparison:{ballMassKg:number;heightM:number};base:{peakHeightM:number;apexTimeS:number;samples:{t:number;h:number;v:number}[]};sensitivity:{cd:number;heightM:number}[]};
const fmt=(x:number)=>Math.round(x).toLocaleString('en-US');
function currentSample(t:number){
 const list=data.base.samples;
 if(t<=0)return {h:0,v:330};
 if(t>=data.base.apexTimeS)return {h:data.base.peakHeightM,v:0};
 let low=0,high=list.length-1;
 while(low+1<high){const mid=Math.floor((low+high)/2);if(list[mid].t<t)low=mid;else high=mid;}
 const a=list[low],b=list[high],q=clamp((t-a.t)/(b.t-a.t));
 return {h:a.h+(b.h-a.h)*q,v:a.v+(b.v-a.v)*q};
}
const Backdrop:React.FC<{kind:string,frame:number}>=({kind,frame})=>{
 const blue=kind==='sky'||kind==='altitude'||kind==='comparison';
 const background=blue?'linear-gradient(150deg,#224970,#6A96B3 55%,#B3D9EF)':'radial-gradient(circle at 50% 30%,#445268,#131B2D 60%,#030813)';
 return <AbsoluteFill style={{background,overflow:'hidden'}}>
 {Array.from({length:10},(_,i)=><div key={i} style={{position:'absolute',top:70+i*205,left:(i%2===0?-200:550)+Math.sin(frame/54+i)*70,width:600,height:150,borderRadius:'50%',filter:'blur(46px)',background:blue?'#FFFFFF66':'#9DBDD633',opacity:blue?.4:.18}}/>)}
 <div style={{position:'absolute',inset:0,background:'linear-gradient(180deg,#030916A3 0%,transparent 26%,#03091780 69%,#01040BDC 100%)'}} />
 </AbsoluteFill>;
};
const Bullet:React.FC<{x:number,y:number,rot?:number,scale?:number}>=({x,y,rot=0,scale=1})=><svg viewBox="0 0 450 140" style={{position:'absolute',width:450*scale,height:140*scale,left:x,top:y,transform:'rotate('+rot+'deg)',filter:'drop-shadow(0 16px 24px #000C)'}}>
 <defs><linearGradient id="metal" x1="0" y1="0" x2="0" y2="1"><stop stopColor="#FFF0BD"/><stop offset=".45" stopColor="#C18E4F"/><stop offset="1" stopColor="#553924"/></linearGradient></defs>
 <path d="M28 30L286 30Q365 33 421 70Q365 107 286 110L28 110Z" fill="url(#metal)" stroke="#F8E6BE" strokeWidth="5"/>
 <rect x="12" y="20" width="30" height="100" rx="6" fill="#9A6839"/>
 <path d="M45 47 L290 47" stroke="#FFEDBF" strokeWidth="7" opacity=".7"/>
 </svg>;
const Gun:React.FC<{frame:number}>=({frame})=><svg viewBox="0 0 1000 950" style={{position:'absolute',top:630,left:25,width:1030,height:980,transform:'rotate('+(Math.sin(frame/8)*.4)+'deg)',filter:'drop-shadow(0 20px 50px #000)'}}>
  <g transform="translate(30,210)">
   <path d="M65 40H930L975 60V150H470L402 230L295 605L125 534L222 208H75Z" fill="#252B34" stroke="#A5B7C8" strokeWidth="12"/>
   <rect x="330" y="16" width="197" height="181" rx="25" fill="#333945" stroke="#B3C8D8" strokeWidth="8"/>
   <circle cx="427" cy="109" r="76" fill="#111A29" stroke="#9FB1C9" strokeWidth="11"/>
   <path d="M256 546L356 228" stroke="#976A43" strokeWidth="112"/>
   <path d="M540 180Q490 370 390 245" fill="none" stroke="#B5C6D8" strokeWidth="18"/>
  </g>
 </svg>;
const Bowling:React.FC<{progress:number}>=({progress})=><svg viewBox="0 0 930 810" style={{width:930,height:810}}>
 <defs><radialGradient id="ball"><stop stopColor="#636E86"/><stop offset=".7" stopColor="#172337"/><stop offset="1" stopColor="#050A15"/></radialGradient></defs>
 <path d="M200 85V720" stroke={Y} strokeWidth="9" strokeDasharray="19 14"/>
 <path d="M182 104L200 76L218 104M182 696L200 724L218 696" stroke={Y} strokeWidth="10" fill="none"/>
 <text x="30" y="437" fontSize="67" fill={Y} fontWeight="900">12m</text>
 <path d="M250 722H850" stroke={W} strokeWidth="14"/>
 <circle cx="550" cy={95+610*ease(progress)} r="103" fill="url(#ball)" stroke="#C8D1E0" strokeWidth="10"/>
 <circle cx="516" cy={57+610*ease(progress)} r="13" fill="#020510"/>
 <circle cx="571" cy={57+610*ease(progress)} r="13" fill="#020510"/>
 <circle cx="545" cy={113+610*ease(progress)} r="13" fill="#020510"/>
 <text x="680" y="220" fontSize="52" fill={W} fontWeight="900">約4.7kg</text>
 <text x="400" y="780" fontSize="39" fill={Y} fontWeight="800">エネルギー量の比較</text>
 </svg>;
const Meter:React.FC<{h:number,v:number}>=({h,v})=><div style={{padding:35,width:860,borderRadius:30,background:'#06162CE8',border:'3px solid #FFFFFF3B'}}>
 {[['高度',fmt(h)+' m',h/data.base.peakHeightM],['上昇速度',v.toFixed(1)+' m/s',v/330]].map(([title,val,ratio],i)=><div key={String(title)} style={{marginBottom:i===0?37:0}}>
 <div style={{display:'flex',justifyContent:'space-between',fontSize:43,fontWeight:900}}><span>{title}</span><span style={{color:i===0?Y:R}}>{val}</span></div>
 <div style={{height:29,background:'#43556E',borderRadius:18,overflow:'hidden',marginTop:18}}><div style={{height:'100%',width:(clamp(Number(ratio))*100)+'%',background:i===0?Y:R,borderRadius:18}}/></div>
 </div>)}
 </div>;
const Comparison:React.FC<{p:number}>=({p})=><div style={{width:880,padding:35,background:'#071629DB',borderRadius:26}}>
 {data.sensitivity.map((item,i)=><div key={item.cd} style={{marginBottom:31}}>
 <div style={{fontSize:39,fontWeight:800,display:'flex',justifyContent:'space-between'}}><span>Cd = {item.cd.toFixed(2)}</span><span style={{color:i===1?Y:W}}>{fmt(item.heightM)}m</span></div>
 <div style={{height:34,background:'#273F59',marginTop:13,borderRadius:15,overflow:'hidden'}}><div style={{background:i===1?Y:'#6CA9D3',height:'100%',width:(100*item.heightM/1200*ease(p))+'%',borderRadius:15}}/></div>
 </div>)}
 </div>;
const Visual:React.FC<{kind:string,frame:number,p:number}>=({kind,frame,p})=>{
 if(kind==='revolver')return <Gun frame={frame}/>;
 if(kind==='bullet')return <Bullet x={100+620*ease(p)} y={840} scale={.95}/>;
 if(kind==='bowling')return <div style={{position:'absolute',top:790,left:65}}><Bowling progress={p}/></div>;
 if(kind==='sky')return <Bullet x={340} y={1390-680*ease(p)} rot={-90-Math.sin(frame/10)*10} scale={.9}/>;
 if(kind==='altitude'){
  const simT=data.base.apexTimeS*ease(p),s=currentSample(simT);
  return <><Bullet x={320} y={1130-235*(s.h/data.base.peakHeightM)} rot={-90+Math.sin(frame/12)*7} scale={.75}/>
  <div style={{position:'absolute',top:1280,left:90}}><Meter h={s.h} v={s.v}/></div></>;
 }
 if(kind==='comparison')return <div style={{position:'absolute',top:890,left:105}}><Comparison p={p}/></div>;
 return <Bullet x={330} y={790+130*ease(p)} rot={-90+Math.sin(frame/7)*12} scale={.85}/>;
};
export const MagnumV9:React.FC<Props>=({withAudio=false,assets=[]})=>{
 const frame=useCurrentFrame(),{fps}=useVideoConfig();
 const idx=Math.max(0,chapters.findIndex(s=>frame>=s.start*fps&&frame<s.end*fps));
 const s=chapters[idx],local=frame-s.start*fps,p=clamp(local/((s.end-s.start)*fps));
 const entry=spring({fps,frame:local,config:{damping:16,stiffness:125}});
 const color=idx===0||idx===6?R:Y;
 const muteApex=frame>=Math.floor(33.5*fps)&&frame<Math.floor(34.15*fps);
 return <AbsoluteFill style={{fontFamily:'Meiryo, Yu Gothic, sans-serif',color:W}}>
   {assets[idx]?<AbsoluteFill><OffthreadVideo muted src={staticFile('assets/'+assets[idx])} style={{height:'100%',width:'100%',objectFit:'cover',filter:'brightness(.65) contrast(1.12) saturate(1.07)'}} /></AbsoluteFill>:<Backdrop kind={s.kind} frame={frame}/>}
   <Visual kind={s.kind} frame={local} p={p}/>
   <div style={{position:'absolute',inset:0,background:'linear-gradient(180deg,#02050DC9 0%,transparent 32%,#02040B16 57%,#02050EEA 85%)'}}/>
   <div style={{position:'absolute',top:97,left:62,right:62}}>
    <div style={{fontWeight:900,fontSize:33,color:Y}}>ラテラルシンキング / IF SCIENCE</div>
    <div style={{height:10,background:'#FFFFFF45',marginTop:30,borderRadius:9,overflow:'hidden'}}><div style={{height:'100%',background:Y,width:(100*frame/TOTAL)+'%'}}/></div>
    <div style={{fontSize:52,marginTop:85,fontWeight:900,textShadow:'0 6px 30px #000',transform:'translateY('+(50*(1-entry))+'px)',opacity:entry}}>{s.title}</div>
    <div style={{fontSize:idx===2?81:idx===0?92:idx===4?132:100,fontWeight:900,marginTop:31,lineHeight:1.3,color,textShadow:'0 8px 38px #000'}}>{s.big}</div>
   </div>
   <div style={{position:'absolute',bottom:278,left:60,right:60,padding:'29px 34px',fontSize:idx===2?35:40,fontWeight:800,textAlign:'center',lineHeight:1.4,background:'#081626E8',borderRadius:24,border:'2px solid #FFFFFF28'}}>{s.caption}</div>
   <div style={{position:'absolute',bottom:149,left:65,right:65,fontSize:26,textAlign:'center',color:M}}>
    {idx===2?'※位置エネルギーの量のみ比較。衝突による作用は異なります。':idx===4?'※無風・鉛直・一定Cdの単純化モデル。実射の予測ではない。':idx===6?'※最高点で鉛直速度0。回転・姿勢は停止しません。':'※映像は安全なVFX。実射・捕獲・物の落下実験は行わない。'}
   </div>
   <div style={{position:'absolute',bottom:68,right:67,fontSize:28,fontWeight:900,color:Y}}>{idx+1} / {chapters.length}</div>
   {withAudio?<Audio src={staticFile('narration.wav')} />:null}
   {withAudio?<Audio src={staticFile('bgm.wav')} volume={(f)=>{if(f>=1000&&f<=1030)return 0;return Math.min(.10,Math.min(1,f/20)*.10);}} loop/>:null}
 </AbsoluteFill>;
};
