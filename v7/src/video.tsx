import React from 'react';
import {AbsoluteFill,Audio,interpolate,spring,staticFile,useCurrentFrame,useVideoConfig} from 'remotion';
export const FPS=30;
const scenes=[
 {seconds:5,label:'人生の赤信号',line:'毎日の信号待ち',big:'人生で何日？',kind:'city',note:'通勤する人生をフェルミ推定'},
 {seconds:5,label:'前提① 信号機の数',line:'1日あたり',big:'20か所',kind:'signals',note:'往復で20か所と仮定'},
 {seconds:5,label:'前提② 赤信号の確率',line:'赤で止まる確率',big:'41%',kind:'gauge',note:'41%は推定条件であり統計値ではない'},
 {seconds:5,label:'前提③ 停車する時間',line:'赤信号1回',big:'60秒',kind:'clock',note:'平均60秒の停止を仮定'},
 {seconds:6,label:'まずは1日分',line:'20 × 41% × 60秒',big:'8.2分',kind:'equation',note:'492秒、つまり1日約8.2分'},
 {seconds:6,label:'40年間で計算',line:'240日 × 40年',big:'78,720分',kind:'calendar',note:'年間240日の通勤を40年間'},
 {seconds:7,label:'人生に換算すると',line:'78,720 ÷ 1,440',big:'約55日',kind:'life',note:'54.67日を四捨五入'},
 {seconds:7,label:'時間の使い道',line:'人生の55日間',big:'あなたなら？',kind:'end',note:'その時間を何に使いたい？'}
];
export const TOTAL_FRAMES=scenes.reduce((a,s)=>a+s.seconds*FPS,0);
const starts=scenes.map((_,i)=>scenes.slice(0,i).reduce((a,s)=>a+s.seconds*FPS,0));
const cap=(a:number)=>Math.max(0,Math.min(1,a));
const gold='#FFD55B',red='#FF6560',pale='#F6F8FE',grey='#B7C6D7';
const building=(x:number,y:number,w:number,h:number)=><g key={x}><rect x={x} y={y} width={w} height={h} fill="#16263A" stroke="#41546E" strokeWidth={3}/>{Array.from({length:7},(_,j)=><rect key={j} x={x+22+(j%2)*58} y={y+48+Math.floor(j/2)*94} width={20} height={31} fill={j%3===0?'#E8B36C':'#57708B'} opacity={.64}/>)}</g>;
const Background:React.FC<{frame:number}>=({frame})=>{
 const shift=Math.sin(frame/46)*22;
 return <AbsoluteFill style={{background:'radial-gradient(circle at 50% 26%,#314358,#101D2E 52%,#070D17 100%)',overflow:'hidden'}}>
  <div style={{position:'absolute',inset:-100,backgroundImage:'linear-gradient(90deg,#ffffff06 1px,transparent 1px),linear-gradient(#ffffff06 1px,transparent 1px)',backgroundSize:'74px 74px',transform:'translate('+shift+'px,0)'}}/>
  <svg viewBox="0 0 1080 1920" style={{position:'absolute',width:'100%',height:'100%',transform:'translate('+shift*.25+'px,0)'}}>
    {building(0,320,230,810)}{building(172,460,205,650)}{building(790,230,290,950)}{building(932,500,210,670)}
    <path d="M460 960 L640 960 L1180 1920 L-100 1920Z" fill="#172437"/>
    {Array.from({length:5},(_,i)=><rect key={i} x={528-i*15} y={1090+i*170} width={24+i*30} height={60+i*13} rx={4} fill="#D7CA9B" opacity={.55}/>)}
    <g transform="translate(726,395)"><rect x="43" y="0" width="16" height="670" fill="#8191A2"/><rect x="0" y="0" rx="22" width="113" height="310" fill="#0A101B" stroke="#8293A8" strokeWidth="8"/>
      {[0,1,2].map((i)=><circle key={i} cx={56} cy={59+i*96} r={36} fill={i===0?red:'#252F39'} opacity={i===0?.90+.1*Math.sin(frame/10):1}/>)}
    </g>
  </svg>
  <div style={{position:'absolute',inset:0,background:'linear-gradient(180deg,#050A16D9,transparent 25%,#060C19A3 62%,#060C19E6)'}}/>
 </AbsoluteFill>
};
const boxStyle:React.CSSProperties={background:'#09172DDE',border:'2px solid #FFFFFF28',borderRadius:30,padding:34,boxShadow:'0 15px 60px #000B'};
const Visual:React.FC<{kind:string;frame:number;local:number;seconds:number}>=({kind,frame,local,seconds})=>{
 const progress=cap(local/37);
 if(kind==='gauge'){
   const r=208,circ=2*Math.PI*r;
   return <svg width="600" height="600" viewBox="0 0 600 600"><circle cx="300" cy="300" r={r} fill="#0B1D31" stroke="#41516A" strokeWidth="40"/><circle cx="300" cy="300" r={r} fill="none" stroke={red} strokeWidth="40" strokeLinecap="round" strokeDasharray={(circ*.41*progress)+' '+circ} transform="rotate(-90 300 300)"/><text x="300" y="325" textAnchor="middle" fontSize="130" fontWeight="900" fill={gold}>{Math.round(41*progress)}%</text></svg>;
 }
 if(kind==='clock'){
   const a=local/FPS*Math.PI*2;
   return <svg width="600" height="600" viewBox="0 0 600 600"><circle cx="300" cy="300" r="244" fill="#122237" stroke={pale} strokeWidth="16"/>{Array.from({length:12},(_,i)=>{const t=i*Math.PI/6;return <line key={i} x1={300+199*Math.sin(t)} y1={300-199*Math.cos(t)} x2={300+222*Math.sin(t)} y2={300-222*Math.cos(t)} stroke={gold} strokeWidth="10"/>})}<line x1="300" y1="300" x2={300+179*Math.sin(a)} y2={300-179*Math.cos(a)} stroke={red} strokeWidth="15" strokeLinecap="round"/><line x1="300" y1="300" x2="378" y2="241" stroke={pale} strokeWidth="13" strokeLinecap="round"/><circle cx="300" cy="300" r="21" fill={gold}/></svg>;
 }
 if(kind==='signals')return <div style={{width:810,display:'grid',gridTemplateColumns:'repeat(5,1fr)',gap:17}}>{Array.from({length:20},(_,i)=><div key={i} style={{height:120,border:'3px solid #718199',borderRadius:24,background:'#071426DB',display:'flex',alignItems:'center',justifyContent:'center',opacity:i<Math.ceil(20*progress)?1:.15}}><div style={{width:56,height:56,borderRadius:'50%',background:i%2===0?red:gold,boxShadow:'0 0 18px #FF645A66'}}/></div>)}</div>;
 if(kind==='calendar')return <div style={{width:790,display:'grid',gridTemplateColumns:'repeat(7,1fr)',gap:12,...boxStyle}}>{Array.from({length:35},(_,i)=><div key={i} style={{height:84,borderRadius:12,background:i<35*progress?gold:'#3D536B',display:'flex',alignItems:'center',justifyContent:'center',fontWeight:900,fontSize:37,color:i<35*progress?'#0B1726':pale}}>{i+1}</div>)}</div>;
 if(kind==='life')return <div style={{width:900,...boxStyle}}><div style={{fontSize:42,marginBottom:32,color:pale}}>約55日分の時間</div><div style={{height:85,borderRadius:40,background:'#43576D',overflow:'hidden'}}><div style={{height:'100%',width:(100*progress)+'%',background:'linear-gradient(90deg,'+red+','+gold+')',borderRadius:40}}/></div><div style={{fontSize:31,color:grey,marginTop:25}}>毎日8.2分の積み重ね</div></div>;
 if(kind==='equation')return <div style={{width:900,textAlign:'center',...boxStyle}}><div style={{fontSize:57,fontWeight:800}}>20 × 0.41 × 60</div><div style={{fontSize:103,fontWeight:900,color:gold,marginTop:40}}>{Math.round(492*progress)}秒</div><div style={{fontSize:36,color:grey}}>＝ 約8.2分</div></div>;
 return <div style={{width:890,textAlign:'center',...boxStyle}}><div style={{fontSize:57,fontWeight:900,color:gold}}>時間を、数字で考える。</div><div style={{fontSize:35,marginTop:25,color:grey}}>前提を変えれば、結論も変わる。</div></div>;
};
export const LateralV7:React.FC<{withAudio?:boolean}>=({withAudio=false})=>{
 const frame=useCurrentFrame(),{fps}=useVideoConfig();
 const index=Math.max(0,starts.findIndex((start,i)=>frame>=start&&frame<start+scenes[i].seconds*fps));
 const sc=scenes[index],local=frame-starts[index];
 const entrance=spring({fps,frame:local,config:{damping:18,stiffness:110}});
 const offset=interpolate(entrance,[0,1],[105,0]);
 return <AbsoluteFill style={{fontFamily:'Meiryo, Yu Gothic, sans-serif',color:pale}}>
  <Background frame={frame}/>
  <AbsoluteFill style={{padding:'110px 70px'}}>
   <div style={{fontSize:31,color:grey,fontWeight:800}}>ラテラルシンキング　　<span style={{color:gold}}>FERMI / 07</span></div>
   <div style={{height:9,background:'#41536A',borderRadius:9,marginTop:34,overflow:'hidden'}}><div style={{width:(100*frame/TOTAL_FRAMES)+'%',height:'100%',background:gold}}/></div>
   <div style={{position:'absolute',top:285,left:35,right:35,textAlign:'center',transform:'translateY('+offset+'px)',opacity:entrance}}>
    <div style={{fontSize:54,fontWeight:800,color:pale}}>{sc.label}</div>
    <div style={{fontSize:76,fontWeight:900,marginTop:53,textShadow:'0 8px 30px #000'}}>{sc.line}</div>
    <div style={{fontSize:121,fontWeight:900,color:index===6?red:gold,marginTop:12,textShadow:'0 9px 35px #000'}}>{sc.big}</div>
   </div>
   <div style={{position:'absolute',top:845,left:0,right:0,display:'flex',justifyContent:'center',alignItems:'center',height:640,transform:'scale('+(0.92+0.08*entrance)+')',opacity:cap(local/12)}}>
    <Visual kind={sc.kind} frame={frame} local={local} seconds={sc.seconds}/>
   </div>
   <div style={{position:'absolute',bottom:205,left:60,right:60,background:'#09192ADB',borderRadius:22,padding:'26px 32px',fontSize:34,color:grey,textAlign:'center'}}>{sc.note}</div>
   <div style={{position:'absolute',bottom:105,right:70,color:gold,fontSize:30,fontWeight:800}}>{index+1} / {scenes.length}</div>
  </AbsoluteFill>
  {withAudio?<Audio src={staticFile('narration.wav')}/>:null}
 </AbsoluteFill>;
};
