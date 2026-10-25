import React from 'react';
import {AbsoluteFill,Audio,OffthreadVideo,interpolate,spring,staticFile,useCurrentFrame,useVideoConfig} from 'remotion';

type Props={withAudio?:boolean;assets?:string[]};
const chapters=[
 {start:0,end:7,label:'結論から始める',top:'次元のマグナム弾',big:'素手でキャッチできる？',sub:'水平に撃たれたら、まず不可能',shot:'revolver'},
 {start:7,end:16,label:'水平発射のフェルミ推定',top:'弾丸 約10.2g × 330m/s',big:'約555 J',sub:'E = ½ × 0.0102kg × (330m/s)²',shot:'bullet'},
 {start:16,end:25,label:'真上に撃ったら？',top:'重力 ＋ 空気抵抗',big:'速度は低下',sub:'空気抵抗があると上昇中に減速する',shot:'sky'},
 {start:25,end:35,label:'空気抵抗も計算',top:'単純化した抗力モデル',big:'約500〜1,100m',sub:'Cd=0.3〜1.0 / 理想的な鉛直飛翔',shot:'clouds'},
 {start:35,end:45,label:'物理学の結論',top:'最高点では鉛直速度',big:'0 m/s',sub:'一瞬だけ停止。ただし回転や落下は続く',shot:'apex'}
] as const;
const FPS=30;
const yellow='#FFD45D',white='#F6F7FC',pale='#BBD0E3',red='#FF5C63';
const lim=(v:number)=>Math.max(0,Math.min(1,v));
const rise=(p:number)=>1-Math.pow(1-lim(p),3);

const Sky:React.FC<{frame:number;chapter:number}>=({frame,chapter})=>{
 const gradient=chapter<2?'radial-gradient(circle at 60% 22%,#536172,#171C2B 52%,#050810 95%)':'linear-gradient(180deg,#19466F,#527CA0 38%,#8BB2CB 65%,#CDDDE9)';
 return <AbsoluteFill style={{background:gradient,overflow:'hidden'}}>
   {Array.from({length:11},(_,i)=>{
     const y=190+i*154,dx=Math.sin(frame*.008+i)*48;
     return <div key={i} style={{position:'absolute',left:(i%2===0?-120:580)+dx,top:y,width:520,height:120,background:'#E1ECF4',opacity:chapter<2?.045:.07,borderRadius:'50%',filter:'blur(37px)'}}/>;
   })}
   {chapter<2?<div style={{position:'absolute',bottom:0,width:'100%',height:630,background:'linear-gradient(0deg,#050A13 15%,transparent 100%)'}}/>:null}
 </AbsoluteFill>;
};
const Bullet:React.FC<{t:number;f:number;mode:'horizontal'|'vertical'|'apex'}>=({t,f,mode})=>{
 const x=mode==='horizontal'?160+t*650:500+Math.sin(f*.02)*10;
 const y=mode==='vertical'?1600-1090*(1-Math.pow(1-t,2)):mode==='apex'?660+Math.max(0,(t-.6))*240:870;
 const rotation=mode==='horizontal'?0:-90;
 return <svg style={{position:'absolute',inset:0,width:'100%',height:'100%',filter:'drop-shadow(0 20px 22px #0009)'}} viewBox="0 0 1080 1920">
 <g transform={'translate('+x+','+y+') rotate('+rotation+')'}>
  <path d="M-155 -37 L100 -37 Q148 -24 175 0 Q148 24 100 37 L-155 37Z" fill="#CC954F" stroke="#FFE2A2" strokeWidth="6"/>
  <rect x="-176" y="-41" width="34" height="82" rx="7" fill="#885A30"/>
  <path d="M-155 -25L95 -25" stroke="#F9DAA1" strokeWidth="7" opacity=".8"/>
 </g></svg>;
};
const Gun:React.FC<{frame:number}>=({frame})=><svg viewBox="0 0 1080 1920" style={{position:'absolute',inset:0,width:'100%',height:'100%',filter:'drop-shadow(0 19px 34px #000)'}}>
   <g transform={'translate(115,'+(760+Math.sin(frame/17)*7)+') rotate(-11)'}>
    <path d="M40 60H850L925 40V142H475L392 215L290 490L145 435L240 205H80Z" fill="#20232A" stroke="#A7B4C3" strokeWidth="9"/>
    <rect x="330" y="26" width="170" height="142" rx="20" fill="#34383F" stroke="#B7C5D5" strokeWidth="10"/>
    <circle cx="414" cy="96" r="61" fill="#111822" stroke="#94A6B8" strokeWidth="8"/>
    <path d="M250 455L350 209" stroke="#85613C" strokeWidth="100"/>
    <path d="M522 145Q470 330 382 246" fill="none" stroke="#8DA2B6" strokeWidth="15"/>
   </g>
   <path d="M130 515 Q420 170 780 490 L775 635 L230 690Z" fill="#02050A" opacity=".93"/>
   <rect x="155" y="494" width="685" height="42" rx="15" fill="#090D14"/>
 </svg>;
const Meter:React.FC<{value:number}>=({value})=><div style={{width:860,background:'#071326CD',padding:34,borderRadius:32,border:'2px solid #FFFFFF34'}}>
  <div style={{display:'flex',justifyContent:'space-between',fontSize:36,fontWeight:800,marginBottom:20}}><span>推定速度</span><span style={{color:yellow}}>{Math.round(value)} m/s</span></div>
  <div style={{height:35,background:'#46566B',borderRadius:18,overflow:'hidden'}}><div style={{height:'100%',width:(Math.max(0,Math.min(100,value/330*100)))+'%',background:'linear-gradient(90deg,#F05B60,#FFD45D)',borderRadius:18}}/></div>
 </div>;
const Chart:React.FC<{progress:number}>=({progress})=><svg viewBox="0 0 950 425" style={{width:950,height:425,background:'#0A152BCF',borderRadius:24}}>
  <path d="M105 45V350H880" fill="none" stroke="#C6D3E4" strokeWidth="6"/>
  <text x="30" y="36" fontSize="32" fill={pale}>速度</text><text x="807" y="398" fontSize="32" fill={pale}>時間</text>
  <path d="M105 72Q370 170 810 348" fill="none" stroke={yellow} strokeWidth="10" strokeDasharray="12 10"/>
  <circle cx={105+705*progress} cy={72+276*rise(progress)} r="19" fill={red} stroke="white" strokeWidth="5"/>
 </svg>;
const Panel:React.FC<{chapter:number;local:number}>=({chapter,local})=>{
 const t=lim(local/((chapters[chapter].end-chapters[chapter].start)*FPS));
 if(chapter===0)return <Gun frame={local}/>;
 if(chapter===1)return <Bullet f={local} t={t} mode="horizontal"/>;
 if(chapter===2)return <Bullet f={local} t={t} mode="vertical"/>;
 if(chapter===3)return <div style={{position:'absolute',top:1130,left:65}}><Chart progress={t}/></div>;
 return <Bullet f={local} t={t} mode="apex"/>;
};
export const Magnum45:React.FC<Props>=({withAudio=false,assets=[]})=>{
 const frame=useCurrentFrame();
 const {fps}=useVideoConfig();
 const chapter=Math.max(0,chapters.findIndex(s=>frame>=s.start*fps&&frame<s.end*fps));
 const sc=chapters[chapter],local=frame-sc.start*fps,total=sc.end-sc.start;
 const progress=lim(local/(total*fps));
 const enter=spring({frame:local,fps,config:{damping:19,stiffness:110}});
 const dim=chapter<=1?'#070A12':'#09233D';
 const opacity=interpolate(enter,[0,1],[0,1]);
 const showAlt=chapter===3;
 const val=chapter===2?330*Math.pow(1-progress,1.9):chapter===3?330*(1-progress):chapter===4?0:330;
 return <AbsoluteFill style={{fontFamily:'Meiryo, Yu Gothic, sans-serif',color:white,background:dim}}>
  {assets[chapter]?<AbsoluteFill><OffthreadVideo src={staticFile('assets/'+assets[chapter])} muted style={{height:'100%',width:'100%',objectFit:'cover',filter:'brightness(.52) contrast(1.13) saturate(.75)'}} /></AbsoluteFill>:<Sky frame={frame} chapter={chapter}/>}
  <Panel chapter={chapter} local={local}/>
  <div style={{position:'absolute',inset:0,background:'linear-gradient(180deg,#01040BBB,transparent 29%,#01040B10 56%,#02040BE8 90%)',pointerEvents:'none'}}/>
  <div style={{position:'absolute',left:72,right:72,top:94}}>
    <div style={{fontSize:36,fontWeight:900,letterSpacing:3,color:yellow}}>ラテラルシンキング / 物理学</div>
    <div style={{height:11,marginTop:32,background:'#65758970',borderRadius:10,overflow:'hidden'}}><div style={{height:'100%',width:(100*frame/1350)+'%',background:yellow}}/></div>
    <div style={{fontSize:43,fontWeight:900,marginTop:75,opacity,transform:'translateY('+(45*(1-enter))+'px)'}}>{sc.label}</div>
    <div style={{fontSize:65,fontWeight:900,marginTop:30,textShadow:'0 5px 25px #000'}}>{sc.top}</div>
    <div style={{fontSize:showAlt?100:chapter===0?79:114,fontWeight:900,marginTop:24,color:chapter===4?red:yellow,textShadow:'0 6px 25px #000',letterSpacing:-2}}>{sc.big}</div>
  </div>
  {chapter===2||chapter===3?<div style={{position:'absolute',left:100,bottom:610}}><Meter value={val}/></div>:null}
  {chapter===4?<div style={{position:'absolute',left:118,right:118,bottom:660,textAlign:'center',fontSize:47,color:red,fontWeight:900}}>速度が0でも安全ではない</div>:null}
  <div style={{position:'absolute',left:62,right:62,bottom:264,padding:'29px 36px',border:'2px solid #FFF3',background:'#071224DE',borderRadius:27,fontSize:40,fontWeight:800,textAlign:'center',lineHeight:1.42}}>
   {sc.sub}
  </div>
  <div style={{position:'absolute',left:72,right:72,bottom:143,fontSize:26,color:pale,textAlign:'center'}}>
   {chapter===3?'Cdの仮定に依存する概算。実射の弾道予測ではありません。':
    chapter===4?'※完全鉛直・無風の理想モデル。落下弾にも危険があります。':
    '※すべてCG・VFXによる説明。実射や捕獲をしないでください。'}
  </div>
  {withAudio?<Audio src={staticFile('narration.wav')} />:null}
 </AbsoluteFill>;
};
